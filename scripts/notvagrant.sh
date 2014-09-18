#!/bin/bash
# notvagrant.sh is the creation of Julien Desfossez

if test $# -lt 1; then
	echo "Usage : $0 <hostname> [deploy-script] [deploy-script-params]"
	exit 1
fi

sudo lxc-ls -f | grep $1 >/dev/null
if test $? = 0; then
	echo -n "Already exists, destroy it (Y/n) ? "
	read a
	if test "$a" = 'n'; then
		exit 0
	else
		sudo lxc-stop -n $1
		sudo lxc-destroy -n $1
	fi
fi

sudo lxc-create -n $1 -t ubuntu
sudo lxc-start -d -n $1

ip=""
while test "$ip" = "" -o "$ip" = "-"; do
	ip=$(sudo lxc-info -n $1 -i -H)
done
ssh-keygen -f "$HOME/.ssh/known_hosts" -R $ip

ok=0
while test $ok = 0; do
	ssh -oBatchMode=yes -oStrictHostKeyChecking=no root@$ip uname -a
	if test $? = 0; then
		ok=1;
	fi
done

if test ! -z $2; then
	scp $2 root@$ip:
	p=$(basename $2)
	ssh root@$ip "chmod +x $p; ./$p $3"
fi
echo "Your machine is ready at $ip"
exit 0