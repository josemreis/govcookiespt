#!/bin/bash

# must set expressvpn activation code as an environmental variable, export ACTIVATION_CODE="..."
# helper for destroying all virtual machines
destroy_machines() {
    LOCATIONS="pt,esba,denu,usny,in" vagrant destroy -f &>/dev/null
    LOCATIONS="pt,esba,denu,usny,in" vagrant global-status --prune &>/dev/null
    rm -rf ../.vagrant
}

## run 
# destroy existing machines
# destroy_machines
 

# this crawl will use all websites in the sample, so it should take a very long time
scripts_array=(
    'bash scripts/vagrant-run-audits.sh --replications 2 --locations "pt,esba" --name-prefix "audit" --activation-code ${ACTIVATION_CODE} --n-websites 10 --vpn -headless' # pt v. es (Barcelona)
    'bash scripts/vagrant-run-audits.sh --replications 2 --locations "pt,denu" --name-prefix "audit" --activation-code ${ACTIVATION_CODE} --n-websites 10 --vpn -headless' # pt v. de (Nuremberg)
    'bash scripts/vagrant-run-audits.sh --replications 2 --locations "pt,usny" --name-prefix "audit" --activation-code ${ACTIVATION_CODE} --n-websites 10 --vpn -headless' # pt v. us (NY)
    'bash scripts/vagrant-run-audits.sh --replications 2 --locations "pt,in" --name-prefix "audit" --activation-code ${ACTIVATION_CODE} --n-websites 10 --vpn -headless'   # pt v. in 
)

for cur_script in "${scripts_array[@]}"; do
    # destroy existing machines
    destroy_machines
    for attempt in {1..10}; do
        eval $cur_script
        ret=$?
        if [ $ret -eq 0 ]; then
            break
        else
            echo "script failed, retrying..."
            sleep 40
        fi
    done
done

# destroy existing machines
destroy_machines
