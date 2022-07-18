#!/bin/bash

## display usage
show_help() {
    cat <<EOF
usage: $0 PARAM [-r|--replications] [-l|--locations] [-p|--name-prefix] [-headless] [-b | --browser-n] [-h|--help]

Run multiple tracking audits on governmental websites from Portugal with varying geo-locations (expressvpn) and controlling for the maximum number of cookies

OPTIONS:
   PARAM        The param
   -h|--help    Show this message
   -r|--replications Number of times to replicate a trial given a location
   -l|--locations Comma separated locations using expressvpn aliases
   -p|--name-prefix Trial name prefix
   -b | --browser-n Number of browsers to user per audit
   -headless Should the trial be ran in headless mode?

RELEVANT CONSTANTS:
    LOCATION_WITHOUT_VPN If you do not want to use a vpn client, please define the current location using this constant
    MAX_COOKIES Define the maximum number of cookies to use in the max cookies control trial
EOF

}

## initialize some vars
# prepare the array with the target geo-locations
LOCATIONS=""
LOCATION_WITHOUT_VPN="pt"
REPS=1
TRIAL_NAME_PREFIX="audit"
HEADLESS=0
BROWSER_N=1
MAX_COOKIES=5000
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
    -l | --locations)
        if [ "$2" ]; then
            LOCATIONS=($(echo "$2" | tr "," "\n"))
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
start_vpn() {
    echo "Start vpn"
    vpn_con_status=$(expressvpn status)
    if [[ "$vpn_con_status" -ne *"Not connected"* ]]; then
        if [[ "$current_alias" -eq "$1" ]]; then
            echo "Already connected to $1"
            exit 1
        else
            # disconnect from previous
            disconnect_from_vpn

        fi
        # connect
        expressvpn connect $1
    fi
}

disconnect_from_vpn() {
    expressvpn disconnect
    sleep 20
    wget -q --tries=10 --timeout=20 --spider http://google.com
    if [[ $? -ne 0 ]]; then
        notify-send 'Will disconnect from the internet in 40 secs...'
        sleep 40
        nmcli networking off
        nmcli networking on
        sleep 30
    fi
}

prepare_script() {
    # arg 1: is_max_cookies: 0 if base, 1 if max cookies

    # prepare the template
    script_template='python3 run_audits.py -name "${name_prefix}" -l "${loc}"'
    # if headless, add the flag
    if [[ $HEADLESS -gt 0 ]]; then
        script_template="${script_template} -headless"
    fi
    # add the script specific flags
    if [[ $1 -gt 0 ]]; then
        tmp_script=$(name_prefix="${TRIAL_NAME_PREFIX}_max_cookies_rep_${i}_${HS}" loc="$loc" envsubst <<<"$script_template")
        relevant_script="${tmp_script} --max-cookies ${MAX_COOKIES}"
    else
        relevant_script=$(name_prefix="${TRIAL_NAME_PREFIX}_rep_${i}_${HS}" loc="$loc" envsubst <<<"$script_template")
    fi
    final_script="${relevant_script} -b ${BROWSER_N}"
    echo $final_script

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

### Run
## Preparation before running
# wd at grand parent dir
cd "$(dirname $(dirname "$0"))"
# # # activate openwpm conda environment
# source ~/miniconda3/etc/profile.d/conda.sh
eval "$(conda shell.bash hook)"
conda activate openwpm

# hostname
HS=$(echo $HOSTNAME)
# current alias empty var
current_alias=""
# replications loop
for i in $(eval echo {1..$REPS}); do
    echo "TRIAL RUN $i"
    if [ -z "$LOCATIONS" ]; then
        # set to the user defined location without vpn
        LOCATIONS=(
            $LOCATION_WITHOUT_VPN
        )
        NO_VPN=1
    else
        # shuffle locations
        LOCATIONS=($(shuf -e "${LOCATIONS[@]}"))
        NO_VPN=0
    fi
    # loop across the different locations and assign to the relevant flag
    for loc in "${LOCATIONS[@]}"; do
        # check if connected to the internet
        wget -q --tries=10 --timeout=20 --spider http://google.com
        ## if yes, go on...
        if [[ $? -eq 0 ]]; then
            if [[ "$NO_VPN" -gt 0 ]]; then
                start_vpn $loc
                current_alias=$loc
            fi
            echo "Started running $loc crawlers" 
            run_scripts
            echo "Finished running $loc crawlers"
            if [[ "$NO_VPN" -eq 0 ]]; then
                disconnect_from_vpn
            fi
        fi
    done
done