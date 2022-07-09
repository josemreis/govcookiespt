# govcookiespt
Measure third-party tracking in Portuguese governmental websites using OpenWPM.

## Table of contents <!-- omit in toc -->

- [govcookiespt](#govcookiespt)
  - [Set up](#set-up)
    - [Instalation](#instalation)
    - [openwpm conda environment](#openwpm-conda-environment)

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
