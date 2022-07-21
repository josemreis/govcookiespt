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
  config.vm.synced_folder "./", "/home/vagrant/", type: "rsync", owner: "vagrant", rsync_auto: true, rsync__exclude: ['./OpenWPM/', './miniconda3/', './.git/']

  # install dependencies, miniconda3, and set up the openwpm environment
  config.vm.provision "shell", inline: <<-SHELL

    set -e

    ## repositories
    echo ""
    echo "[+] Installing ubuntu dependencies"
    echo ""

    sudo apt-get clean -qq 
    sudo apt-get update -qq
    sudo apt-get -y upgrade -qq
  
    ## installing dependencies
    sudo apt-get install -y libterm-readkey-perl ca-certificates wget curl git expect iproute2 procps libnm0 make npm -qq
    
    npm -g install npm@latest
    
    # see: https://serverfault.com/questions/500764/dpkg-reconfigure-unable-to-re-open-stdin-no-file-or-directory/670688#670688
    export DEBIAN_FRONTEND=noninteractive

    echo ""
    echo "[+] Installing firefox and xvfb"
    echo ""

    ## installing firefox and xvfb 
    sudo apt-get install -y firefox xvfb -qq

    echo ""
    echo "[+] Installing miniconda3"
    echo ""

    ## installing conda
    # https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    miniconda=Miniconda3-latest-Linux-x86_64.sh
    wget --quiet https://repo.anaconda.com/miniconda/$miniconda
    sudo bash $miniconda -b -p /home/miniconda3
    source /home/miniconda3/etc/profile.d/conda.sh
    hash -r
    export PATH="/home/miniconda3/bin:$PATH"
    echo 'export PATH="/home/miniconda3/bin:$PATH"' >> /home/.bashrc
    source ~/.bashrc
    source /home/.bashrc
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
    # store it in opt to avoid the symlink issues in the shared folder known to occur in virtualbox machines
    cd /opt
    git clone https://github.com/openwpm/OpenWPM.git
    # permissions for openwpm to all users
    sudo chmod -R a+rwx OpenWPM
  SHELL

  config.vm.provision "shell", privileged: false, inline: <<-SHELL
      ## install conda environment and dependencies
      echo ""
      echo "> Building the openwpm conda environment"
      echo ""

      cd /opt/OpenWPM 
      # fix unlink issues
      # npm cache clean --force
      # paths_array=(
      #   "Extension/firefox"
      #   "Extension/webext-instrumentation"
      # )
      # old_dir=$(pwd)
      # for p in "${path_array[@]}"; do
      #   cd p
      #   ls -l .
      #   pwd
      #   if [ -d "node_modules" ]; then
      #     rm -rf node_modules
      #   fi
      #   if [ -f "package-lock.json" ]; then
      #       rm package-lock.json
      #   fi
      #   cd $old_dir
      # done

      source /home/miniconda3/etc/profile.d/conda.sh
      # Make conda available to shell script
      eval "$(conda shell.bash hook)"
      if [ "$1" != "--skip-create" ]; then
        echo 'Creating / Overwriting openwpm conda environment.'
        # `PYTHONNOUSERSITE` set so python ignores local user site libraries when building the env
        # See: https://github.com/openwpm/OpenWPM/pull/682#issuecomment-645648939
        PYTHONNOUSERSITE=True conda env create --force -q -f environment.yaml
      fi
      echo 'Activating environment.'
      conda activate openwpm
      # ls -l /home/miniconda3/envs/
      # rm -rf /home/miniconda3/envs/openwpm/lib/node_modules/npm/node_modules/
      # npm cache clean --force
      echo 'Installing firefox.'
      ./scripts/install-firefox.sh
      echo 'Building extension.'
      ./scripts/build-extension.sh
      echo 'Installation complete, activate your new environment by running:'
      echo 'conda activate openwpm'
  SHELL

  # install and activate expressvpn
  config.vm.provision "shell", path: "scripts/install-expressvpn.sh", env: {"ACTIVATION_CODE" => ENV['ACTIVATION_CODE']}

  # virtual machine provider configs
  config.vm.provider :libvert do |v|
    v.driver = "kvm"
    v.memory = 4096
    v.cpus = 2
  end
end
