#!/bin/bash
# check install pkg
clear
if [[ $(dpkg -s rfkill | grep "Status") != *"Status: install ok installed"* ]]; then
  echo -e "\033[31m pkg rfkill not installed \033[0m"
  sudo apt install rfkill -y
fi

if [[ $(dpkg -s wireless-tools | grep "Status") != *"Status: install ok installed"* ]]; then
  echo -e "\033[31m pkg wireless-tools not installed \033[0m"
  sudo apt install wireless-tools -y
fi

if [[ $(dpkg -s net-tools | grep "Status") != *"Status: install ok installed"* ]]; then
  echo -e "\033[31m pkg net-tools not installed \033[0m"
  sudo apt install net-tools -y
fi




# start scrypt
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo $DIR
cd "$DIR"

echo "1 - Connect    Wi-Fi
0 - Disconnect Wi-Fi"

read -n 1 Connection

echo " "

sudo ifconfig wlan0 up

if [[ $Connection == "1" ]]; then
  rfkill unblock wifi
  iwlist wlan0 scan | grep "LEGIT | NewLocation"

  echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
  update_config=1
  country=UA

  network={
          ssid=\"LEGIT | NewLocation\"
          priority=1
          scan_ssid=1
          key_mgmt=WPA-PSK
          psk=9503ea330d997092c820a3c57ea9768c3f38c9ce3f56185468c0f7ad0f478613
  }" > wpa_supplicant.conf
  sudo mv $DIR/wpa_supplicant.conf /etc/wpa_supplicant/
  sudo wpa_supplicant -B -c /etc/wpa_supplicant/wpa_supplicant.conf -i wlan0
  sudo dhclient wlan0
  sleep 5s
  echo "IP Address: $(ifconfig wlan0 | awk '$1 == "inet" {print $2}')"
fi

if [[ $Connection == "0" ]]; then
  sudo ifconfig wlan0 down
  rfkill block wifi
  sleep 5s
  dev_name="eth0"
  echo "IP Address: $(ifconfig $dev_name | awk '$1 == "inet" {print $2}')"
fi






