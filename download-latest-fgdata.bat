REM This Windows script downloads latest files from GitLab: Nasal folder, and the version file.

@echo off

if exist FGROOT (
    rmdir /S /Q FGROOT
)

mkdir FGROOT
cd FGROOT || exit /b

git clone --filter=blob:none --depth 1 --no-checkout https://gitlab.com/flightgear/fgdata.git FGDATA
cd FGDATA || exit /b

git sparse-checkout init --no-cone
git sparse-checkout set /Nasal /version
git checkout next

rmdir /S /Q .git
