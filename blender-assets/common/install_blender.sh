#!/usr/bin/env bash
set -euo pipefail
root="${1:-$HOME/.cache/hf-blender}"
mkdir -p "$root"
file=blender-4.5.14-linux-x64.tar.xz
url="https://download.blender.org/release/Blender4.5/$file"
curl -fL --retry 2 "$url" -o "$root/$file"
printf '%s  %s\n' 9ba871ff2ecd36526b77432745980b7e6664ecd0c7ca11c48849073dcfe06da3 "$root/$file" | sha256sum -c -
tar -xJf "$root/$file" -C "$root"
"$root/blender-4.5.14-linux-x64/blender" --version
