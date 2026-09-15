#!/usr/bin/env bash
# Runs the EditMode suite headlessly and prints a per-test summary.
# Deletes the previous results first so a compile failure cannot look like a pass.
export PATH="$PATH:/c/Users/Akrem/AppData/Local/Unity/bin"
PROJ="C:/Users/Akrem/Desktop/Projects/Fallow"
R="$PROJ/test-results.xml"
LOG="$PROJ/Logs/unity-test-run.log"

rm -f "$R"
mkdir -p "$PROJ/Logs"

unity test "$PROJ" --editor-version 6000.3.24f1 --mode EditMode \
  --format json --no-banner --non-interactive --timeout 2400 >"$LOG" 2>&1
CLI_EXIT=$?

if [ ! -f "$R" ]; then
  echo "NO RESULTS FILE (unity exit $CLI_EXIT) - the editor did not get as far as running tests."
  echo "This is almost always a C# compile error. CLI output:"
  tail -40 "$LOG"
  echo "---- compile errors from the editor log ----"
  grep -haE "error CS[0-9]+" "$LOCALAPPDATA/Unity/Editor/Editor.log" 2>/dev/null | sort -u | head -30
  exit 2
fi

grep -oE 'total="[0-9]+" passed="[0-9]+" failed="[0-9]+"[^>]*inconclusive="[0-9]+" skipped="[0-9]+"' "$R" | head -1
echo "---- results ----"
python - "$R" <<'PY'
import sys, xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
cases = list(root.iter('test-case'))
for tc in sorted(cases, key=lambda t: t.get('fullname') or ''):
    print(f"{tc.get('result'):9} {tc.get('fullname')}")
print('---- failures ----')
n = 0
for tc in cases:
    if tc.get('result') != 'Passed':
        n += 1
        print('FAIL:', tc.get('fullname'))
        f = tc.find('failure')
        if f is not None:
            for tag in ('message', 'stack-trace'):
                e = f.find(tag)
                if e is not None and e.text:
                    print('   ', e.text.strip()[:1500])
if n == 0:
    print('(none)')
PY
