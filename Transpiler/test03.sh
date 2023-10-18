#!/bin/dash
# Format taken from course forum

SHEEPY_PATH="${HOME}/code/comp2041/assignments/ass2/sheepy.py"
INPUT_PATH="$(pwd)/input03.sh"

expected_output="$(mktemp)"
transpiled_output="$(mktemp)"
actual_output="$(mktemp)"

trap 'rm -f "$expected_output" "$actual_output" "$transpiled_output"' EXIT

"$INPUT_PATH" > "$expected_output"
python3 "$SHEEPY_PATH" "$INPUT_PATH" > "$transpiled_output"
python3 "$transpiled_output" > "$actual_output"

echo 'Testing globbing inside a subprocess..'
if ! diff -u "$expected_output" "$actual_output" >/dev/null 2>&1
then
    echo 'Test failed: Actual output different from expected output'
else
    echo 'Test passed'
fi




