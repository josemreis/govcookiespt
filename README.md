# govcookiespt
Measure third-party tracking in Portuguese governmental websites using OpenWPM.

## Table of contents <!-- omit in toc -->

- [govcookiespt](#govcookiespt)
  - [Set up](#set-up)
    - [Instalation](#instalation)
    - [openwpm conda environment](#openwpm-conda-environment)
    - [Vagrant](#vagrant)
  - [Running the tracking audits](#running-the-tracking-audits)
    - [The `run_audits.py` CLI tool](#the-run_auditspy-cli-tool)
    - [Customised trial scripts i): running a multi-country audit using expressvpn and vagrant](#customised-trial-scripts-i-running-a-multi-country-audit-using-expressvpn-and-vagrant)
    - [Customised trial scripts ii): running a single country audit (no vpn)](#customised-trial-scripts-ii-running-a-single-country-audit-no-vpn)

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

### The `run_audits.py` CLI tool

A CLI tool for running tracking audits on websites associated with the portuguese state. 

```shell
usage: run_audits [-h] [-ss] [-ps] [-l [LOCATION]] [-headless] [-n [WEBSITES_N]] [-b BROWSER_N] [-mc [MAX_COOKIES]] [-name [TRIAL_NAME]] [-s [PATH_TO_SEED_PROFILE]]
                  [-r [RANDOM_SEED]]

Run a tracking audit.

options:
  -h, --help            show this help message and exit
  -ss, --store-screenshots
                        Should it take and store screenshots?
  -ps, --store-source   Should it extract and store the html documents of the pages visited?
  -l [LOCATION], --location [LOCATION]
                        Location used alias. Used for directory naming, does not actually start a vpn.
  -headless             Run headless?
  -n [WEBSITES_N], --n-websites [WEBSITES_N]
                        Number of websites to use in the audit
  -b BROWSER_N, --browser-n BROWSER_N
                        Number of browsers to use
  -mc [MAX_COOKIES], --max-cookies [MAX_COOKIES]
                        As a stoping rule, define a maximum number of cookies a bot is allowed to set. Once reached, the crawl will stop.
  -name [TRIAL_NAME], --trial-name [TRIAL_NAME]
                        Trail name to be used as a prefix to the name of the directory/db/profile of the crawl session
  -s [PATH_TO_SEED_PROFILE], --seed-profile [PATH_TO_SEED_PROFILE]
                        Path to a compressed firefox profile to be used as the seed profile, e.g. 'profile_archive/clean_seed/profile.tar'
  -r [RANDOM_SEED], --random-seed [RANDOM_SEED]
                        Random state seed integer to use while sampling. 
```


### Customised trial scripts i): running a multi-country audit using expressvpn and vagrant

This script will create various vagrant machines with miniconda3, openwpm, and expressvpn installed - if the user provides the expressvpn activation code in the environment variable `ACTIVATION_CODE`.

Then for it will run tracking audits in parallel in two vagrant machines with different vpn connections. As is, it will always combine a vpn connection to portugal with another country. As of now, I am using "Spain (Barcelona)", "Germany (Nuremberg)", "US (NY)", and "India".

```shell
export ACTIVATION_CODE="...."
bash scripts/run-multi-country-trials.sh
```

### Customised trial scripts ii): running a single country audit (no vpn)

This script will run a tracking audit without any vpn connection 10 times (replications...).

```shell
bash scripts/run-single-country-trial.sh
```