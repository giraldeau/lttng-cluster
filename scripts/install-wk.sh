#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

source /etc/lsb-release
if [ "$DISTRIB_ID" != "Ubuntu" ]; then
	echo "ERROR: Only Ubuntu is supported."
	exit 1
fi

# install tools
sudo apt-get update -q
sudo apt-get install -q -y liblttng-ust-dev libsensors4-dev build-essential autoconf automake libtool pkg-config 

test -e ~/workload-kit || git clone https://github.com/giraldeau/workload-kit.git ~/workload-kit
cd ~/workload-kit
./bootstrap
./configure
make -j4
sudo make install
echo "workload-kit installation done"
