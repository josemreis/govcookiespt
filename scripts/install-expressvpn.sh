#!/bin/bash
# ACTIVATION_CODE needs to be set as env var
# export ACTIVATION_CODE={% your-activation-code %}


set -e

echo ""
echo "> Installing expressvpn..."
echo ""

# install
# download the deb file
wget -q "https://www.expressvpn.works/clients/linux/expressvpn_3.27.1.0-1_amd64.deb"
sudo dpkg -i expressvpn_3.27.1.0-1_amd64.deb
rm expressvpn_3.27.1.0-1_amd64.deb

# cp /etc/resolv.conf /tmp/resolv.conf
# su -c 'umount /etc/resolv.conf'
# cp /tmp/resolv.conf /etc/resolv.conf
# sed -i 's/DAEMON_ARGS=.*/DAEMON_ARGS=""/' /etc/init.d/expressvpn
# service expressvpn restart

echo ""
echo "> Checking internet connection..."
echo ""

# check if connected to the internet
wget -q --tries=10 --timeout=20 --spider http://google.com
## if yes, go on...
if [[ $? -eq 0 ]]; then
    echo "[+] Connected"
else 
    echo "[-] No internet connection. Exiting"
    exit -1
fi

echo ""
echo "> Check expressvpn activation code..."
echo ""
if [ -z "$ACTIVATION_CODE" ]
then
    echo ""
    echo "[!] Set ACTIVATION_CODE env var!"
    echo ""
    exit -1
else
    echo ""
    echo "[+] ACTIVATION_CODE env variable is present"
    echo ""
fi
echo ""

echo ""
echo "> Activating expressvpn..."
echo ""
# run the activation script
/usr/bin/expect -c '
spawn expressvpn activate
expect {
    "code:" {
        send "'$ACTIVATION_CODE'\r"
        expect "information."
        send "n\r"
    }
    "Already activated" {send "n\r"}
}
expect eof
'
# restart expressvpn 
sudo service expressvpn restart
sleep 10
# test the activation
echo ""
echo "> Testing the activation..."
echo ""
activation_test="$(expressvpn status)"
if [[ "$activation_test" == *"Not Activated"* ]]
then
    echo "[-]Failed the activation test!"
    echo "Ouput:"
    echo "$activation_test"
    echo "[!]Set ACTIVATION_CODE env var!"
    exit -1
else
    echo "[+] expressvpn activated"
fi
#https://stackoverflow.com/questions/20430371/my-docker-container-has-no-internet
# cp /etc/resolv.conf /tmp/resolv.conf
# su -c 'umount /etc/resolv.conf'
# cp /tmp/resolv.conf /etc/resolv.conf
# sed -i 's/DAEMON_ARGS=.*/DAEMON_ARGS=""/' /etc/init.d/expressvpn
# service expressvpn restart
# set some preferences. As of now they will be constants and not arguments. Could turn them into ENV variables later on
expressvpn preferences set auto_connect true
expressvpn preferences set preferred_protocol auto
expressvpn preferences set lightway_cipher auto
# expressvpn test
# echo ""
# echo "> Testing the vpn connection..."
# echo ""
# vpn_conn_test="$(expressvpn connect pt)"
# sleep 20
# if [[ "$vpn_conn_test" == *"Connected to"* ]]
# then
#     echo "Sucessfully established a vpn connection"
#     # disconnect
#     service expressvpn restart
# else
#     echo "Failed the vpn connection test!"
#     echo "Ouput:"
#     echo "$vpn_conn_test"
#     exit -1
# fi