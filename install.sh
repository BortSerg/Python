#!/bin/bash
wget https://www.python.org/ftp/python/3.10.4/Python-3.10.4.tgz
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev  libncursesw5-dev xz-utils tk-dev
tar xvf Python-3.10.4.tgz
cd Python-3.10.4
./configure --enable-optimizations --with-ensurepip=install
make -j 8
sudo make altinstall

sudo apt install python3-pip
sudo python3 -m pip install --upgrade pip
sudo python3.10 -m pip install --upgrade pip

export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/.local/lib:$PATH"

sudo apt-get update -y
sudo python3 -m pip install pyserial tqdm colorama keyboard
sudo python3.10 -m pip install pyserial tqdm colorama keyboard





