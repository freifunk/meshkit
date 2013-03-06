#!/bin/sh
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
This script will help you in getting a new image from the imagebuilder.
It knows the following options:

	-c Checks if a new version is available
	-h Show this help
	-k Keeps your configuration and all currently installed packages
	-l Lists currently installed packages
	-v Show version of this script

" && exit 1
fi

[ -f /etc/config/imagebuilder ] || (echo "/etc/config/imagebuilder does not exist, exit now."; exit 1)

get_var() {
	uci -q show $1 | cut -d "." -f 2-100 |grep "\." | sed -e 's/^\([a-z_]*\)\./\1_/g' -e 's/=\(.*\)$/="\1"/g'
}

get_option_failed() {
	echo "Could not get option '$1' from /etc/config/imagebuilder, abort."
	exit 1
}

get_version_failed() {
	echo "Could not get $1, abort"
	exit 1
}

while read line; do
	echo $line > /dev/null
	export "${line//\"/}"
done << EOF
`get_var imagebuilder.update`
EOF

server="$(echo $update_url | cut -d / -f 1-3)"
[ -z "$server" ] && get_option_failed url
targets_url="${update_url/wizard.cgi/targets.cgi}"


get_target(){
	target=$(wget -q "$targets_url" -O - 2> /dev/null)
	echo $target | sed 's/ /\n/g' |grep $1
}

targetmain="$(echo $update_target | cut -d "-" -f 1)"
[ -z "$targetmain" ] && get_option_failed target
target=$(get_target $targetmain)
[ -z "$target" ] && echo "Could not get $targets_url, abort." && exit 1
targetversion="$(echo $target | grep $targetmain | sed 's/.*-//')"
test $targetversion -ne 0 2> /dev/null || get_version_failed targetversion
installedversion="$(echo $update_target | sed 's/.*-//')"
test $installedversion -ne 0 2> /dev/null || get_version_failed installedversion

compare_versions(){
	if [ "$targetversion" -gt "$installedversion" ]; then
		echo 1
	else
		echo 0
	fi
}

extract_links() {
	rm -f /tmp/firmwareupdate.links; touch /tmp/firmwareupdate.links
	while read line; do
		if [ -n "$(echo $line |grep -e sysupgrade -e trx -e combined)" ]; then
			echo "$line" | sed -n 's/<li><a href=\"\(.*\)\">.*/\1/p' >> /tmp/firmwareupdate.links
		fi
	done << EOF
$(grep '<li><a href=' /tmp/firmwareupdate.result)
EOF
}

select() {
	n=1
	echo "Select which firmware image you want to download/flash:"
	while read line; do
		line="$(echo $line | sed -n 's/.*\/bin\/\(.*\)$/\1/p')"
		echo "$n$tab$line"
		n=$(( $n +1))
	done < /tmp/firmwareupdate.links

	echo -n "#> "
	read choice
	test $choice -ne 0 2> /dev/null || (echo "Invalid option selected, use a number from the links above." && select)
	if [ $choice -ge $n ]; then
		echo "Invalid option selected, use a number from the links above."; select
	fi
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
		echo "No new version, $update_target is already the newest."
		exit 1
	else
		echo "New version $targetversion is available."
		exit 0
	fi
fi

download () {
	rm -f /tmp/flashme.bin
	wget -q $server/$1 -O /tmp/flashme.bin || (echo "Error: Download of $server/$1 failed, exit."; exit)
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

updatestring="$(uci show imagebuilder |grep -v -e 'update=imagebuilder' -e target -e noconf -e url -e extrapackages | sed 's/imagebuilder.update.//g' |tr '\n' '&')"
[ -z "$updatestring" ] && (echo "No usable config found in /etc/config/imagebuilder, exit now."; exit 1)

if [ "$action" == "keepconf" ]; then
	echo "I'm trying to generate and download your fírmware image now, this may take some time, please be patient."
	echo "$update_url?noconf=1&target=$target&$updatestring&extrapackages=$(list_installed)&cgi_formstatus=GENERATE" | sed 's/ /%20/g'> /tmp/firmwareupdate.url
	wget -q $(cat /tmp/firmwareupdate.url) -O /tmp/firmwareupdate.result
	if [ ! "$?" == "0" ]; then
		echo "Sorry, but the download of the firmware failed."
		echo "The url i tried to fetch was:"
		echo "$update_url?noconf=1&$updatestring&extrapackages=$(list_installed)&cgi_formstatus=GENERATE"
		exit
	fi
	# extract links from firmwareupdate.result
	extract_links
	select

	# Download and flash firmware
	sedcmd="sed ${choice}q;d /tmp/firmwareupdate.links"
	firmwarefile=$($sedcmd)
	echo "Downloading your new firmware now..."
	download $firmwarefile
	confirm_flash
	sysupgrade /tmp/flashme.bin
fi
