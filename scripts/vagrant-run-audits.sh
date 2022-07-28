#!/bin/bash

set -e

## display usage
show_help() {
    cat <<EOF
usage: $0 PARAM [-r|--replications] [-l|--location] [-p|--name-prefix] [-headless] [-k | --activation-code] [-h|--help]

Run multiple tracking audits on governmental websites from Portugal with varying geo-locations (expressvpn) and controlling for the maximum number of cookies

OPTIONS:
   PARAM        The param
   -h|--help    Show this message
   -r|--replications Number of times to replicate a trial given a location
   -l|--locations Comma-separated expressvpn location aliases
   -p|--name-prefix Trial name prefix
   -headless Should the trial be ran in headless mode?
   -k | --activation-code Expressvpn activation code
   -v | --vpn Should it use vpn
   -n | --n-websites Number of websites to crawl, if left empty all websites will be used
EOF

}

## initialize some vars
# prepare the array with the target geo-locations
LOCATIONS=("pt")
REPS=1
TRIAL_NAME_PREFIX="audit"
HEADLESS=0
BROWSER_N=1
USE_VPN=0
MAX_COOKIES=5000
ACTIVATION_CODE=""
N_WEBSITES=3

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
            LOCATIONS="$2"
            shift
        fi
        ;;
    -p | --name-prefix)
        if [ "$2" ]; then
            TRIAL_NAME_PREFIX="$2"
            shift
        fi
        ;;
    -n | --n-websites)
        if [ "$2" ]; then
            N_WEBSITES=$2
            shift
        fi
        ;;
    -k | --activation-code)
        if [ "$2" ]; then
            ACTIVATION_CODE="$2"
            shift
        fi
        ;;
    -v | --vpn)
        let "USE_VPN+=1"
        shift
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

# split the string and convert into an array with the locations/machine names 
LOCATIONS_ARRAY=($(echo "$LOCATIONS" | tr "," "\n"))

### helpers
# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
    echo ""
    echo "[!] Killing all background jobs and exiting..."
    echo ""
    pkill -9 -f "vagrant"
    pkill -9 -f "python3 run_audits.py"
    disconnect_from_vpn
    exit 0
}

start_machines() {

    for loc in "${LOCATIONS_ARRAY[@]}"
    do 
        if LOCATIONS="$LOCATIONS" vagrant status $loc | grep -E -lq "$loc.*running"; then
            echo ""
            echo "[!] Machine $1 already running"
            echo ""
        else
            echo ""
            echo "[+] Creating the $1 virtual machine"
            echo ""
            ACTIVATION_CODE="$ACTIVATION_CODE" LOCATIONS="$LOCATIONS" vagrant up $1 --provision
        fi
    done

}

disconnect_from_vpn() {

    echo ""
    echo "[+] Disconnecting from the vpn in machine $1"
    echo ""
    
    LOCATIONS="$LOCATIONS" vagrant ssh $1 --command "if expressvpn status | grep -lq 'Connected to'; then expressvpn disconnect; fi"
    sleep 40
}

start_vpn() {

    echo ""
    echo "[+] Connecting to the vpn in machine $1"
    echo ""
    LOCATIONS="$LOCATIONS" vagrant ssh $1 --command "expressvpn connect $1"
    sleep 20
}

run_script() {

    # arg 1 expressvpn alias which will be the name of a machine
    # hostname of the host machine for dedupling parallel scripts
    command_prefix="cd /home/vagrant/govcookiespt;"
    # if the user did not define locations, do not use the 
    if [[ $USE_VPN -gt 0 ]]; then
        echo ""
        echo "[+] Using vpn set to '$1'"
        echo ""
        command_final="$command_prefix bash scripts/run-audits.sh --replications ${REPS} --location $1 --name-prefix "${TRIAL_NAME_PREFIX}_${HOSTNAME}" --n-websites ${N_WEBSITES} -headless"
        disconnect_from_vpn $1
        start_vpn $1
    else
        # no vpn
        command_final="$command_prefix bash scripts/run-audits.sh --replications ${REPS} --name-prefix "${TRIAL_NAME_PREFIX}_${HOSTNAME}" --n-websites ${N_WEBSITES} -headless"
    fi
    echo ""
    echo "[+] Running tracking audit in $1"
    echo ""
    echo ""
    echo "[+] Command: $command_final"
    echo ""
    LOCATIONS="$LOCATIONS" vagrant ssh $1 --command "$command_final"
    ret=$?
    if [ $ret -ne 0 ]; then
        # script failed, return an exit code 42 to inform any parent scripts
        exit 42
    fi
    disconnect_from_vpn $1

}

halt_machines() {
    for loc in "${LOCATIONS_ARRAY[@]}"
    do
        # halt the machine
        LOCATIONS="$LOCATIONS" vagrant halt $loc 
    done
}

run_scripts() {
    # launch the vagrant machines if not running, one per location
    start_machines
    for loc in "${LOCATIONS_ARRAY[@]}"
    do
        run_script $loc & # Put a function in the background
    done
    wait

    halt_machines

}

### Run
run_scripts
