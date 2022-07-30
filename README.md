# govcookiespt
Measure third-party tracking in Portuguese governmental websites using OpenWPM.

## Table of contents <!-- omit in toc -->

- [govcookiespt](#govcookiespt)
  - [Set up](#set-up)
    - [Instalation](#instalation)
    - [openwpm conda environment](#openwpm-conda-environment)
    - [Vagrant](#vagrant)
  - [Running the tracking audits](#running-the-tracking-audits)
    - [Running a multi-country audit using expressvpn and vagrant](#running-a-multi-country-audit-using-expressvpn-and-vagrant)
    - [Running a single country audit (no vpn)](#running-a-single-country-audit-no-vpn)

## Set up

### Instalation

Git clone this repository and then install OpenWPM, other OS based dependencies, as well as required python modules. For more details [see](https://github.com/mozilla/OpenWPM). Note that OpenWPM only operates on linux or MAC OS and you need anaconda or miniconda installed in your machine. Open a terminal in this directory and run the following command.

```bash
bash scripts/install_dependencies.sh
```

### openwpm conda environment

`OpenWPM` is built using a conda environment containing all the required dependencies. So before running the scripts or the CLI tool, you will always have to activate it. From the main directory of this repo, open a terminal and run.

```bash
conda activate openwpm
```

### Vagrant

Case you want to run the audits using various geo-locations, you can use the `scripts/vagrant-run-audits.sh`. For this script to work, you will have to have [vagrant](https://www.vagrantup.com/downloads) and [virtualbox](https://www.virtualbox.org/) installed. As of now, the script uses [ExpressVPN](https://www.expressvpn.com/) and so you will need an active subscription and its activation code. 


## Running the tracking audits

### Running a multi-country audit using expressvpn and vagrant

This script will create various vagrant machines with miniconda3, openwpm, and expressvpn installed - if the user provides the expressvpn activation code in the environment variable `ACTIVATION_CODE`.

Then for it will run tracking audits in parallel in two vagrant machines with different vpn connections. As is, it will always combine a vpn connection to portugal with another country. As of now, I am using "Spain (Barcelona)", "Germany (Nuremberg)", "US (NY)", and "India".

```shell
export ACTIVATION_CODE="...."
bash scripts/run-multi-country-trials.sh
```

### Running a single country audit (no vpn)

This script will run a tracking audit without any vpn connection 10 times (replications...).

```shell
bash scripts/run-single-country-trial.sh
```