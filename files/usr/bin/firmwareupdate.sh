#!/bin/sh

. /usr/share/libubox/jshn.sh
. /lib/functions.sh

VERSION="0.0.3"
tab="	"

while getopts chklv OPTION; do
	case ${OPTION} in
		c) action="versioncheck";;
		k) action="keepconf";;
		l) action="list-installed";;
		v) echo firmwareupdate.sh Version: $VERSION; exit 0;;
		\?|h) help=1;;
	esac
done

[ -z "$action" ] && help=1

if [ "$help" = 1 ]; then
echo "
This script will help you in getting a new image from the meshkit.
It knows the following options:

	-c Checks if a new version is available
	-h Show this help
	-k Keeps your configuration and all currently installed packages
	-l Lists currently installed packages
	-v Show version of this script

" && exit 1
fi

config_load meshkit || (echo "/etc/config/meshkit does not exist, exit now."; exit 1)
config_get url "update" url || {
	echo "Update URL not found in /etc/config/meshkit"
	exit 1;
}

config_get target "update" target || {
	echo "Target not found in /etc/config/meshkit"
	exit 1;
}

config_get profile "update" profile
community="$(uci -q get freifunk.community.name)"
config_get url "update" url
server="$(echo $url | cut -d / -f 1-3)"


get_version_failed() {
	echo "Could not get $1, abort"
	exit 1
}


targets_url="$server/api/json/targets"
get_target(){
	MSG=$(wget -q "$targets_url" -O - 2> /dev/null)
        targets="$(echo $MSG | tr -d '[]" ' | sed 's/,/ /g')"
	ret=''
	for t in $targets; do
		if [ -n "$(echo $t | grep $1)" ];then
			if [ "$ret" = '' ]; then
				ret="$t"
			else
				thisversion="$(echo $t | sed -n 's/.*-\(.*\)$/\1/p')"
				retversion="$(echo $ret | sed -n 's/.*-\(.*\)$/\1/p')"
				if [ $retversion -lt $thisversion ]; then
					ret="$t"
				fi
			fi
		fi
	done
	echo $ret
}
installedtarget="$target"
targetmain="$(echo $target | cut -d "-" -f 1)"
target=$(get_target $targetmain)
echo target $target
[ -z "$target" ] && echo "Could not get $targets_url, abort." && exit 1
targetversion="$(echo $target | grep $targetmain | sed 's/.*-//')"

test $targetversion -ne 0 2> /dev/null || get_version_failed targetversion

installedversion="$(echo $installedtarget | sed 's/.*-//')"
test $installedversion -ne 0 2> /dev/null || get_version_failed installedversion
compare_versions(){
	if [ "$targetversion" -gt "$installedversion" ]; then
		echo 1
	else
		echo 0
	fi
}

select() {
	n=1
	echo "Select which firmware image you want to download/flash:"
	for line in $1; do
                if [ -n "$(echo $line |grep -e sysupgrade -e trx -e combined)" ]; then
			echo "$n$tab$line"
			n=$(( $n +1))
		fi
	done

	echo -n "#> "
	read choice
	test $choice -ne 0 2> /dev/null || (echo "Invalid option selected, use a number from the links above." && select)
	if [ $choice -ge $n ]; then
		echo "Invalid option selected, use a number from the links above."; select $1
	fi
        n=1
	for line in $1; do
		if [ -n "$(echo $line |grep -e sysupgrade -e trx -e combined)" ]; then
                	if [ $choice -eq $n ]; then
				firmwareimage="$line"
			fi
			n=$(( $n +1))
		fi
	done

}

confirm_flash() {
	echo -n "Are you really sure you want to flash the new firmware now? [N/y]"
	read confirm
	if [ "$confirm" == "y" ]; then
		echo "I'm flashing your new firmware now. The router will reboot after that."
	else
		echo "You chose to not flash the firmware, i will abort now."
		exit
	fi
}

if [ "$action" == "versioncheck" ]; then
	updateavail=$(compare_versions)
	if [ "$updateavail" == 0 ]; then
		echo "No new version, $target is already the newest."
		exit 1
	else
		echo "New version $targetversion is available."
		exit 0
	fi
fi

download () {
	rm -f /tmp/flashme.bin
	wget -q $1 -O /tmp/flashme.bin || (echo "Error: Download of $server/$1 failed, exit."; exit)
}

list_installed() {
	packages=$(opkg list_installed |awk '{ print $1 }')
	[ ! "$action" == "list-installed" ] && packages=$(echo $packages | sed 's/ /%20/g')
	echo $packages
}

if [ "$action" == "list-installed" ]; then
	list_installed
	exit 0
fi


if [ "$action" == "keepconf" ]; then
	echo "firmwareupgrade.sh $VERSION: Starting firmware upgrade, this may take some time, please be patient."
	echo "$url?noconf=1&target=$target&profile=$profile&packages=$(list_installed)" | sed 's/ /%20/g'> /tmp/firmwareupdate.url

	wget -q "$(cat /tmp/firmwareupdate.url)" -O /tmp/firmwareupdate.result
	firmwareimage=""

	if [ ! "$?" == "0" ]; then
		echo "Sorry, but the download of the firmware failed."
		echo "The url i tried to fetch was:"
		echo "$update_url?noconf=1&target=$target&packages=$(list_installed)"
		exit
	fi

	json_load "$(cat /tmp/firmwareupdate.result)"
	json_get_var "id" id
	json_get_var "errors" errors
	json_get_var "rand" rand

        if [ -z "$id" ]; then
		json_select "errors"
			for e in target rand id; do
		        json_get_var target $e && errormsg="$errormsg $target"
		done
		json_select ..

		echo "Error: $errormsg"
		exit 1
	fi

        status="1"
        while [ "$status" == "1" ]; do

		statusurl="$server/api/json/buildstatus?id=$id&rand=$rand"
		json="$(wget -q "$statusurl" -O - 2> /dev/null)"
		json_load "$json"
                json_get_var status status
                [ "$status" == "0" ] && {
			echo "\o/"
			json_get_var downloaddir downloaddir

			if json_is_a "files" "array"; then
			        json_select "files"
			        i=1
			        while json_is_a $i "string"; do
			                json_get_var "file" $i
			                files="$files $file"
			                i=$(($i + 1))
			        done
			fi
			select "$files"
			echo "Downloading your new firmware now..."
			download "$downloaddir/$firmwareimage"
			confirm_flash
		        sysupgrade /tmp/flashme.bin
		}
                [ "$status" == "1" ] && echo -n .
                [ "$status" == "2" ] && echo "bError building the image"

		sleep 10
	done
fi
