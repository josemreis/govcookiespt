#!/bin/bash
set -e

echo ""
echo "> Installing OpenWPM and other dependencies.."
echo ""


### miniconda3
if [[ -z $(which conda) ]]; then
    echo ""
    echo "> Installing miniconda 3"
    echo ""
    wget -q wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b
fi

### Install OpenWPM
cd "$(dirname $(dirname "$0"))"
## check if it exists
OPENWPM_PATH="OpenWPM"
if [ -d "$OPENWPM_PATH" ]; then
    echo "OpenWPM already installed in $OPENWPM_PATH. Skipping installation"
else 
    echo "Installing OpenWPM"
    git clone https://github.com/openwpm/OpenWPM.git
    #conda create --name <env> --file package_conda.txt
fi
## install conda environment and dependencies
cd OpenWPM 
bash ./install.sh
