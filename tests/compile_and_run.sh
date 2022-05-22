#!/bin/sh

if [ $# -ne 5 ]; then
  echo "Usage: $0 PYTHON_EXECUTABLE PYTHON_SCRIPT SOURCE_FILE C_FILE EXECUTABLE_FILE"
  exit 1
fi

PYTHON_EXECUTABLE=$(realpath -s "$1")
PYTHON_SCRIPT=$(realpath -s "$2")
SOURCE_FILE=$(realpath -s "$3")
C_FILE=$(realpath -s "$4")
EXECUTABLE_FILE=$(realpath -s "$5")

$PYTHON_EXECUTABLE "$PYTHON_SCRIPT" "$SOURCE_FILE" "$C_FILE"
gcc "$C_FILE" -o "$EXECUTABLE_FILE" -Wall -Wextra -Wpedantic

$EXECUTABLE_FILE
