# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|

  # define the base box
  config.vm.box = "generic/ubuntu1804"

  # synced folder configs
  config.vm.synced_folder "./", "/home/vagrant/govcookiespt", type: "rsync", owner: "vagrant", rsync_auto: true, rsync__exclude: ['./OpenWPM/', './miniconda3/', './.git/']
  # install system dependencies
  config.vm.provision "shell", inline: <<-SHELL
    set -e
    set -x # Print commands and their arguments as they are executed.

    ## repositories
    echo ""
    echo "[+] Installing ubuntu dependencies"
    echo ""

    apt-get clean -qq 
    apt-get update -qq
    apt-get -y upgrade -qq
  
    ## installing dependencies
    apt-get install -y libterm-readkey-perl ca-certificates wget curl git expect iproute2 procps libnm0 make npm -qq
    
    # npm -g install npm@latest
    
    # see: https://serverfault.com/questions/500764/dpkg-reconfigure-unable-to-re-open-stdin-no-file-or-directory/670688#670688
    export DEBIAN_FRONTEND=noninteractive

    echo ""
    echo "[+] Installing firefox and xvfb"
    echo ""

    ## installing firefox and xvfb 
    apt-get install -y firefox xvfb -qq
  SHELL
  # install minicoda3
  config.vm.provision "shell", inline: <<-SHELL

    set -e
    set -x # Print commands and their arguments as they are executed.

    echo ""
    echo "[+] Installing miniconda3"
    echo ""

    ## installing conda
    # https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    miniconda=Miniconda3-latest-Linux-x86_64.sh
    wget --quiet https://repo.anaconda.com/miniconda/$miniconda
    bash $miniconda -b -p /home/miniconda3
    hash -r
    export PATH="/home/miniconda3/bin:$PATH"
    echo 'export PATH="/home/miniconda3/bin:$PATH"' >> /home/.bashrc
    source /home/.bashrc
    echo "conda path: $(which conda)"
    conda config --set always_yes yes --set changeps1 no
    conda update -q conda
    conda info -a
    ## cloning OpenWPM
    # git clone openwpm if missing
    cd /home/vagrant/govcookiespt
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
    git clone https://github.com/openwpm/OpenWPM.git
    # fix permissions issue
    rm -rf OpenWPM/.git
    chmod -R a+rwx OpenWPM
    chown -R $USER OpenWPM
    chown -R $USER /home/miniconda3
  SHELL
  # build the openwpm environment
  config.vm.provision "shell", privileged: false, inline: <<-SHELL

      set -e 
      set -x # Print commands and their arguments as they are executed.

      ## install conda environment and dependencies
      echo ""
      echo "> Building the openwpm conda environment"
      echo ""

      cd /home/vagrant/govcookiespt/OpenWPM 
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
