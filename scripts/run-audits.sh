#!/bin/bash

## display usage
show_help() {
    cat <<EOF
usage: $0 PARAM [-r|--replications] [-l|--location] [-p|--name-prefix] [-headless] [-b | --browser-n] [-n | --n-websites] [-h|--help]

Run multiple tracking audits on governmental websites from Portugal with varying geo-locations (expressvpn) and controlling for the maximum number of cookies

OPTIONS:
   PARAM        The param
   -h|--help    Show this message
   -r|--replications Number of times to replicate a trial given a location
   -l|--location Expressvpn location alias
   -p|--name-prefix Trial name prefix
   -b | --browser-n Number of browsers to user per audit
   -headless Should the trial be ran in headless mode?
   -n | --n-websites Number of websites to crawl, if left empty all websites will be used

RELEVANT CONSTANTS:
    MAX_COOKIES Define the maximum number of cookies to use in the max cookies control trial
EOF

}

## initialize some vars
# prepare the array with the target geo-locations
LOCATION=""
REPS=1
TRIAL_NAME_PREFIX="audit"
HEADLESS=0
BROWSER_N=1
N_WEBSITES=""

## parse the arguments
while true; do
    case $1 in
    -h | --help)
        show_help
        exit 0
        ;;
    -r | --replications)
        if [ "$2" ]; then
            REPS=$2
            shift
        fi
        ;;
    -l | --location)
        if [ "$2" ]; then
            LOCATION="$2"
            shift
        fi
        ;;
    -n | --n-websites)
        if [ "$2" ]; then
            N_WEBSITES="$2"
            shift
        fi
        ;;
    -p | --name-prefix)
        if [ "$2" ]; then
            TRIAL_NAME_PREFIX="$2"
            shift
        fi
        ;;
    -b | --browser-n)
        if [ "$2" ]; then
            BROWSER_N=$2
            shift
        fi
        ;;
    -headless)
        let "HEADLESS+=1"
        shift
        ;;
    *)
        break
        ;;
    esac
    shift
done

### helpers
prepare_script() {
    # arg 1: is_max_cookies: 0 if base, 1 if max cookies

    # prepare the template
    script_template='python3 run_audits.py -name "${name_prefix}" -l "${loc}"'
    # add the headless and n-websites flags
    if [[ $HEADLESS -gt 0 ]]; then
        script_template="${script_template} -headless"
    fi
    if [ -n $N_WEBSITES ]; then
        script_template="${script_template} -n $N_WEBSITES"
    fi
    # add the script specific flags
    if [[ $1 -gt 0 ]]; then
        tmp_script=$(name_prefix="${TRIAL_NAME_PREFIX}_max_cookies_rep_${i}_${HS}" loc="${LOCATION}" envsubst <<<"$script_template")
        relevant_script="${tmp_script} --max-cookies ${MAX_COOKIES}"
    else
        relevant_script=$(name_prefix="${TRIAL_NAME_PREFIX}_rep_${i}_${HS}" loc="${LOCATION}" envsubst <<<"$script_template")
    fi
    final_script="${relevant_script} -b ${BROWSER_N}"
    echo $final_script

}

run_script() {

    # make the scripts
    script_1=$(prepare_script 0)
    # script_2=$(prepare_script 1)
    # prepare a string to be dynamically evaluated in which both scripts are ran in parallel
    # final_cmd=$"${script_1} & ${script_2} && fg"
    final_cmd=$script_1
    echo -e "Running commands:\n$final_cmd"
    # run it
    eval $final_cmd
}

run_scripts() {

    # make the scripts
    script_1=$(prepare_script 0)
    script_2=$(prepare_script 1)
    # prepare a string to be dynamically evaluated in which both scripts are ran in parallel
    final_cmd=$"${script_1} & ${script_2} && fg"
    echo -e "Running commands:\n$final_cmd"
    # run it
    eval $final_cmd
}

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
    echo "Exiting..."
    echo "Killing all background jobs"
    pkill -9 -f "python3 run_audits.py"
    disconnect_from_vpn
    exit 0
}

## Run
## Preparation before running
# wd at grand parent dir relative to this script
cd "$(dirname $(dirname "$0"))"
# # # activate openwpm conda environment
source /home/miniconda3/etc/profile.d/conda.sh
# source ~/miniconda3/etc/profile.d/conda.sh
eval "$(conda shell.bash hook)"
conda activate openwpm

# hostname
HS=$(echo $HOSTNAME)
# replications loop
for i in $(eval echo {1..$REPS}); do
    echo "TRIAL RUN $i"
    # check if connected to the internet
    wget -q --tries=10 --timeout=20 --spider http://google.com
    ## if yes, go on...
    if [[ $? -eq 0 ]]; then
        echo "Started running $LOCATION crawler, run number $i" 
        run_script
        echo "Finished running $LOCATION crawler, run number $i"
    fi
done
