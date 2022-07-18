#!/bin/bash

set -e
set -x

echo ""
echo "> Installing OpenWPM and other dependencies.."
echo ""

### Install OpenWPM
# if [ `logname` = "vagrant" ]; then
#     cd "/vagrant"
# else 
#     cd "$(dirname $(dirname "$0"))"
# fi

## check if it exists
OPENWPM_PATH="OpenWPM"
if [ -d "$OPENWPM_PATH" ]; then
    echo ""
    echo "[!] OpenWPM already installed in $OPENWPM_PATH. Skipping installation"
    echo ""
else 
    echo ""
    echo "> Installing OpenWPM"
    echo ""
    git clone https://github.com/openwpm/OpenWPM.git
    #conda create --name <env> --file package_conda.txt
fi

## install conda environment and dependencies
echo ""
echo "> Building the openwpm conda environment"
echo ""
cd OpenWPM 
# Make conda available to shell script
eval "$(conda shell.bash hook)"
chmod +x ./install.sh
./install.sh
