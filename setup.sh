#!/bin/bash
# run setup.sh IP_ADDR:PORT on startup 
# If connected to the internet: create a proxy on port 80 to $1
# if not connected : Create a proxy to localhost:5000 & start wifi_setup server on port 81

set -o nounset
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" 
cd $DIR

sudo dnsmasq -R -C ./dnsmasq.conf 

sleep 4

if ping -I wlan0 -q -c 1 -W 1 8.8.8.8 >/dev/null; then
    echo "Forward to public server"
    sudo socat TCP-LISTEN:80,fork TCP-CONNECT:$1 &

    if ping -I eth0 -q -c 1 -W 1 8.8.8.8 >/dev/null; then
        echo "Both eth0 and wlan0 connected "
    else 
        exit 0;
    fi

else 
    echo "Forward to local server"
    sudo socat TCP-LISTEN:80,fork TCP-CONNECT:127.0.0.1:5000 &
    
    sudo ./wifi_setup.py &
fi

echo "Setup hotspot"
sudo ip addr flush dev wlan0
sudo ip link set dev wlan0 up
sudo ip addr add 10.0.0.1/8 dev wlan0 
sudo hostapd -B ./hostapd.conf



