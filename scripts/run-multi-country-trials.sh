#!/bin/bash

# must set expressvpn activation code as an environmental variable, export ACTIVATION_CODE="..."

# this crawl will use all websites in the sample, so it should take a very long time
scripts_array=(
    'bash scripts/vagrant-run-audits.sh --replications 3 --locations "pt,esba" --name-prefix "audit" --activation-code ${ACTIVATION_CODE} --vpn -headless' # pt v. es
    'bash scripts/vagrant-run-audits.sh --replications 3 --locations "pt,denu" --name-prefix "audit" --activation-code ${ACTIVATION_CODE} --vpn -headless' # pt v. de
    'bash scripts/vagrant-run-audits.sh --replications 3 --locations "pt,usny" --name-prefix "audit" --activation-code ${ACTIVATION_CODE} --vpn -headless' # pt v. us
    'bash scripts/vagrant-run-audits.sh --replications 3 --locations "pt,in" --name-prefix "audit" --activation-code ${ACTIVATION_CODE} --vpn -headless'   # pt v. in
)

for cur_script in "${scripts_array[@]}"; do
    eval $cur_script
done
