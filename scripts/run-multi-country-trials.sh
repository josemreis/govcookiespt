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
    'bash scripts/vagrant-run-audits.sh --replications 1 --locations "pt,esba" --name-prefix "audit_${audit_n}" --activation-code ${ACTIVATION_CODE} --vpn -headless' # pt v. es (Barcelona)
    'bash scripts/vagrant-run-audits.sh --replications 1 --locations "pt,denu" --name-prefix "audit_${audit_n}" --activation-code ${ACTIVATION_CODE} --vpn -headless' # pt v. de (Nuremberg)
    'bash scripts/vagrant-run-audits.sh --replications 1 --locations "pt,usny" --name-prefix "audit_${audit_n}" --activation-code ${ACTIVATION_CODE}  --vpn -headless' # pt v. us (NY)
    'bash scripts/vagrant-run-audits.sh --replications 1 --locations "pt,in" --name-prefix "audit_${audit_n}" --activation-code ${ACTIVATION_CODE} --vpn -headless'   # pt v. in 
)
audit_n=0
for cur_script in "${scripts_array[@]}"; do
    # destroy existing machines before each run to save up some memory
    destroy_machines
    # add the audit id to the audit name prefix argument
    let "audit_n+=1"
    to_run=$(audit_n="country_dyad_${audit_n}" envsubst <<<"$cur_script")
    # add the dyad id
    for attempt in {1..10}; do
        eval $to_run
        ret=$?
        if [ $ret -eq 0 ]; then
            break
        else
            echo "script failed, retrying in 40 seconds..."
            destroy_machines
            sleep 40
        fi
    done
done

# destroy existing machines
destroy_machines
