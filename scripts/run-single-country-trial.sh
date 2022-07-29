#!/bin/bash

echo "[!] This trial will not use any vpn"

# retry loop
audit_n=0
for attempt in {1..10}; do
    let "audit_n+=1"
    bash scripts/run-audits.sh --replications 10 --location "pt" --name-prefix "audit_novpn_${audit_n}"
    ret=$?
    if [ $ret -eq 0 ]; then
        break
    else
        echo "script failed, retrying in 40 seconds..."
        sleep 40
    fi
done
