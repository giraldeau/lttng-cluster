#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

source /etc/lsb-release
if [ "$DISTRIB_ID" != "Ubuntu" ]; then
	echo "ERROR: Only Ubuntu is supported."
	exit 1
fi

# install tools
apt-get update -q
apt-get install -q -y liblttng-ust-dev libsensors4-dev build-essential autoconf automake libtool 

test -e ~/workload-kit || git clone https://github.com/giraldeau/workload-kit.git ~/workload-kit
cd ~/workload-kit
./bootstrap
make -j4
sudo make install
echo "workload-kit installation done"
