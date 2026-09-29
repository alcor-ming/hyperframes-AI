#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
exec python3 -B "$root/.studio/work_wsl.py" "$@"
