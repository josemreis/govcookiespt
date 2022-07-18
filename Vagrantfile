# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|

  # define the base box
  config.vm.box = "generic/ubuntu2204"

  # synced folder configs
  config.vm.synced_folder "./", "/home/vagrant/", type: "rsync", owner: "vagrant", rsync_auto: true, rsync__exclude: ['./OpenWPM/', './miniconda/', './.git/']
  
  # install dependencies, miniconda3, and set up the openwpm environment
  config.vm.provision "shell", inline: <<-SHELL
    set -e

    # check if the syncing guidelines worked
    echo $(pwd)
    echo $(ls)

    ## repositories
    echo ""
    echo "[+] Installing ubuntu dependencies"
    echo ""

    sudo apt-get clean -qq
    sudo rm -r /var/lib/apt/lists/* -vf 
    sudo apt-get clean -qq 
    sudo apt-get update -qq
    sudo apt-get -y upgrade -qq
  
    ## installing dependencies
    sudo apt-get install -y libterm-readkey-perl ca-certificates wget curl git expect iproute2 procps libnm0 make npm webpack -qq

    echo ""
    echo "[+] Installing firefox and xvfb"
    echo ""

    ## installing firefox and xvfb 
    sudo apt-get install -y  firefox xvfb -qq

    echo ""
    echo "[+] Installing miniconda3"
    echo ""

    ## installing conda
    # https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    miniconda=Miniconda3-latest-Linux-x86_64.sh
    wget --quiet https://repo.anaconda.com/miniconda/$miniconda
    sudo bash $miniconda -b -p /home/vagrant/miniconda3
    export PATH="/home/vagrant/miniconda3/bin:$PATH"
    echo 'export PATH="/home/vagrant/miniconda3/bin:$PATH"' >> /home/vagrant/.bashrc
    source ~/.bashrc
    source /home/vagrant/.bashrc
    echo "conda path: $(which conda)"
    conda config --set always_yes yes --set changeps1 no
    conda update -q conda
    conda info -a

    ## cloning OpenWPM
    # git clone openwpm if missing
    OPENWPM_PATH="OpenWPM"
    ## check if it exists«
    if [ -d "$OPENWPM_PATH" ]; then
        echo ""
        echo "[!] OpenWPM already installed in $OPENWPM_PATH. Removing it."
        echo ""
        rm -rf $OPENWPM_PATH
    fi
    echo ""
    echo "> Installing OpenWPM"
    echo ""
    git clone https://github.com/openwpm/OpenWPM.git
    
    ## install conda environment and dependencies
    echo ""
    echo "> Building the openwpm conda environment"
    echo ""

    cd OpenWPM 
    source /home/vagrant/miniconda3/etc/profile.d/conda.sh
    # create the openwpm environment
    if [ "$1" != "--skip-create" ]; then
      echo 'Creating / Overwriting openwpm conda environment.'
      # `PYTHONNOUSERSITE` set so python ignores local user site libraries when building the env
      # See: https://github.com/openwpm/OpenWPM/pull/682#issuecomment-645648939
      PYTHONNOUSERSITE=True conda env create --force -q -f environment.yaml
    fi
    echo 'Activating environment.'
    # npm config set bin-links false
    npm i npm-force-resolutions
    source /home/vagrant/miniconda3/etc/profile.d/conda.sh
    conda activate openwpm
    sudo bash ./scripts/install-firefox.sh
    # build the extension
    # npm install webpack webpack-dev-server --save-dev
    # npm install --save-dev webpack-cli
    pushd Extension/firefox
    ls
    if [ -d "node_modules" ]; then
      rm -rf node_modules
    fi
    if [ -f "package-lock.json" ]; then
        rm package-lock.json
    fi
    pushd ../webext-instrumentation
    ls
    # fix:https://exerror.com/eresolve-unable-to-resolve-dependency-tree-error-when-installing-npm-packages/
    if [ -d "node_modules" ]; then
      rm -rf node_modules
    fi
    if [ -f "package-lock.json" ]; then
        rm package-lock.json
    fi
    sudo npm cache clean --force
    sudo npm install --legacy-peer-deps
    popd
    sudo npm run build
    popd
    echo "Success: Extension/firefox/openwpm.xpi has been built"
  SHELL

  # install and activate expressvpn
  config.vm.provision "shell", path: "scripts/install-expressvpn.sh", env: {"ACTIVATION_CODE" => ENV['ACTIVATION_CODE']}

  # virtual machine provider configs
  config.vm.provider "virtualbox" do |v|
    v.customize ["setextradata", :id, "VBoxInternal2/SharedFoldersEnableSymlinksCreate/vagrant/syncedfoldername", "1"]
    v.memory = 4096
    v.cpus = 2
  end
end
