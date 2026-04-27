#!/bin/bash

# This Linux script downloads latest files from GitLab: Nasal folder, and the version file.

if [ -d "FGROOT" ]; then
    rm -rf FGROOT
fi

mkdir FGROOT
cd FGROOT || exit

git clone --filter=blob:none --depth 1 --no-checkout https://gitlab.com/flightgear/fgdata.git FGDATA
cd FGDATA || exit

git sparse-checkout init --no-cone
git sparse-checkout set /Nasal /version
git checkout next

rm -rf .git
