#!/usr/bin/env bash
# Runs the EditMode suite headlessly and prints a per-test summary.
export PATH="$PATH:/c/Users/Akrem/AppData/Local/Unity/bin"
PROJ="C:/Users/Akrem/Desktop/Projects/Fallow"
unity test "$PROJ" --editor-version 6000.3.24f1 --mode EditMode \
  --format json --no-banner --non-interactive --timeout 900 >/dev/null 2>&1
R="$PROJ/test-results.xml"
if [ ! -f "$R" ]; then echo "NO RESULTS FILE - editor failed to run"; exit 2; fi
grep -oE 'total="[0-9]+" passed="[0-9]+" failed="[0-9]+"[^>]*inconclusive="[0-9]+" skipped="[0-9]+"' "$R" | head -1
echo "----"
grep -oE '<test-case[^>]*' "$R" | sed -E 's/.*fullname="([^"]*)".*result="([^"]*)".*/\2\t\1/' | grep -v '^<test-case' | sort
echo "---- failures ----"
python - "$R" <<'PY'
import sys,xml.etree.ElementTree as ET
t=ET.parse(sys.argv[1]).getroot()
n=0
for tc in t.iter('test-case'):
    if tc.get('result')!='Passed':
        n+=1
        print('FAIL:', tc.get('fullname'))
        f=tc.find('failure')
        if f is not None:
            for tag in ('message','stack-trace'):
                e=f.find(tag)
                if e is not None and e.text: print('   ', e.text.strip()[:1200])
if n==0: print('(none)')
PY
