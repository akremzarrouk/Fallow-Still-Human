#!/usr/bin/env bash
# Tells one morning as a story, from the shipped data and the unmodified simulation code.
#
#   ./narrate.sh <variant> <seed>   writes Docs/understanding/runs/<variant>-<seed>.md
#   ./narrate.sh --test             runs the narrator's test: daniel_ate_it seed 1 is the baseline's 72 decisions
#
# Builds Tools/narrate-morning together with Assets/_Project/Scripts/Core, using the C#
# compiler and .NET runtime that ship with the project's Unity editor. No Unity process
# is started. If the editor is not where Unity Hub installs it, set UNITY_EDITOR_DATA to
# its Data folder (the one holding NetCoreRuntime and DotNetSdkRoslyn). The build goes to
# Tools/narrate-morning/bin, which git ignores.
#
# Exit codes: 0 done; 1 the test failed; 2 bad arguments or a missing editor or package;
# 3 Windows Application Control blocked the freshly built narrator.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL="$ROOT/Tools/narrate-morning"
BIN="$TOOL/bin"

# Paths handed to the Windows runtime must be Windows paths. Takes any number, one per line out.
native() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$@"; else printf '%s\n' "$@"; fi; }

if [ $# -eq 1 ] && [ "$1" = "--test" ]; then
  MODE=test
elif [ $# -eq 2 ]; then
  MODE=narrate
else
  echo "usage: ./narrate.sh <variant> <seed>   or   ./narrate.sh --test" >&2
  exit 2
fi

VERSION="$(sed -n 's/^m_EditorVersion: *//p' "$ROOT/ProjectSettings/ProjectVersion.txt" | tr -d '\r')"
DATA="${UNITY_EDITOR_DATA:-}"
if [ -z "$DATA" ]; then
  for candidate in "/c/Program Files/Unity/Hub/Editor/$VERSION/Editor/Data" \
                   "C:/Program Files/Unity/Hub/Editor/$VERSION/Editor/Data"; do
    if [ -d "$candidate/NetCoreRuntime" ]; then DATA="$candidate"; break; fi
  done
fi
if [ -z "$DATA" ] || [ ! -d "$DATA/NetCoreRuntime" ] || [ ! -f "$DATA/DotNetSdkRoslyn/csc.dll" ]; then
  echo "Unity $VERSION's editor Data folder was not found. Set UNITY_EDITOR_DATA to it." >&2
  exit 2
fi

DOTNET="$DATA/NetCoreRuntime/dotnet"
[ -f "$DOTNET.exe" ] && DOTNET="$DOTNET.exe"
FRAMEWORK="$(ls -d "$DATA"/NetCoreRuntime/shared/Microsoft.NETCore.App/*/ | sort -V | tail -1)"
FRAMEWORK="${FRAMEWORK%/}"
FRAMEWORK_VERSION="$(basename "$FRAMEWORK")"

JSON="$(ls "$ROOT"/Library/PackageCache/com.unity.nuget.newtonsoft-json@*/Runtime/Newtonsoft.Json.dll 2>/dev/null | head -1 || true)"
if [ -z "$JSON" ]; then
  echo "Newtonsoft.Json.dll was not found under Library/PackageCache. Open the project in Unity once so the package cache exists." >&2
  exit 2
fi

# ---- build: the Core sources as they are, plus the narrator
mkdir -p "$BIN"
RSP="$BIN/build.rsp"
REFS=()
for f in "$FRAMEWORK"/System.*.dll "$FRAMEWORK"/mscorlib.dll "$FRAMEWORK"/netstandard.dll \
         "$FRAMEWORK"/Microsoft.CSharp.dll "$FRAMEWORK"/Microsoft.Win32.Primitives.dll; do
  case "${f##*/}" in *.Native.dll) ;; *) REFS+=("$f") ;; esac
done
REFS+=("$JSON")
SOURCES=()
while IFS= read -r f; do SOURCES+=("$f"); done < <(find "$ROOT/Assets/_Project/Scripts/Core" -name '*.cs' | LC_ALL=C sort)
while IFS= read -r f; do SOURCES+=("$f"); done < <(find "$TOOL" -maxdepth 1 -name '*.cs' | LC_ALL=C sort)
{
  echo "-nologo"
  echo "-target:exe"
  echo "-langversion:9.0"
  echo "-nostdlib"
  echo "-deterministic"
  echo "-out:\"$(native "$BIN/narrate-morning.dll")\""
  native "${REFS[@]}" | sed 's/.*/-r:"&"/'
  native "${SOURCES[@]}" | sed 's/.*/"&"/'
} > "$RSP"

# Built only when a source, a reference or the compiler has changed, so the same file is
# run until then. The build is deterministic: the same inputs give the same bytes.
STAMP="$(cat "$RSP" "${SOURCES[@]}" | sha256sum | cut -d' ' -f1)"
if [ ! -f "$BIN/narrate-morning.dll" ] || [ "$(cat "$BIN/build.stamp" 2>/dev/null)" != "$STAMP" ]; then
  "$DOTNET" "$(native "$DATA/DotNetSdkRoslyn/csc.dll")" -noconfig "@$(native "$RSP")"
  cp "$JSON" "$BIN/Newtonsoft.Json.dll"
  printf '{ "runtimeOptions": { "tfm": "net6.0", "framework": { "name": "Microsoft.NETCore.App", "version": "%s" } } }\n' \
    "$FRAMEWORK_VERSION" > "$BIN/narrate-morning.runtimeconfig.json"
  echo "$STAMP" > "$BIN/build.stamp"
fi

# ---- run
ERR="$BIN/stderr.txt"
set +e
if [ "$MODE" = test ]; then
  "$DOTNET" "$(native "$BIN/narrate-morning.dll")" test "$(native "$ROOT")" 2>"$ERR"
else
  "$DOTNET" "$(native "$BIN/narrate-morning.dll")" narrate "$(native "$ROOT")" "$1" "$2" 2>"$ERR"
fi
CODE=$?
set -e
if [ "$CODE" -ne 0 ] && grep -q "Application Control policy" "$ERR"; then
  echo "Windows Application Control blocked the narrator this script built ($(native "$BIN/narrate-morning.dll"))." >&2
  echo "That is a decision of this machine's security policy about a new, unsigned file; this script does not work around it." >&2
  echo "Nothing was written. Run the command again, or ask whoever manages the policy to allow the file." >&2
  exit 3
fi
cat "$ERR" >&2
exit "$CODE"
