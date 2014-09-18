#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

source /etc/lsb-release
if [ "$DISTRIB_ID" != "Ubuntu" ]; then
	echo "ERROR: Only Ubuntu is supported."
	exit 1
fi

if [ "$(id -u)" != "0" ]; then
	echo "Run this script as root."
	exit 1
fi

# install tools
apt-get update
apt-get install -y lttng-tools babeltrace avahi-utils avahi-daemon git make linux-headers-generic gcc

# install modules
# FIXME: avoid hardcoding the path to the repo
test -e ~/lttng-modules || git clone git://git.dorsal.polymtl.ca/~fgiraldeau/lttng-modules.git ~/lttng-modules
cd ~/lttng-modules
git checkout addons
git pull
make -j4
make modules_install
mkdir -p /usr/local/bin/
install control-addons.sh /usr/local/bin
echo 'search extra updates ubuntu built-in' > /etc/depmod.d/ubuntu.conf
depmod -a

# publish the client with Avahi
cat > /etc/init/avahi-publish-lttng.conf << EOF
start on (started lttng-sessiond and started avahi-daemon)
stop on stopping lttng-sessiond
script
	HOSTNAME=\`hostname -s\`
	avahi-publish -s \$HOSTNAME _lttng._tcp 0
end script
EOF

# startup
control-addons.sh unload
service lttng-sessiond restart
control-addons.sh load
restart avahi-daemon

echo "lttng installation done"
