#!/bin/sh
# Install memory.del skills for the detected hosts. Arguments pass through to install.py,
# e.g. `sh scripts/install.sh --hosts codex` or `--iphone-use ../iPhone-use`.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 "$root/scripts/install.py" "$@"
