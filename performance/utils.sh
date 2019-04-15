# This is a common shell scripts for android adb, am, wms, etc.

function get_package {
	if [[ $# -eq 1 ]]; then
		#statements
		package=$1
		echo "You didn't set the loops, so will use the default loops = 20."
	fi
	# set the loops from input, by default it is set to 20
	if [[ $# -ge 2 ]]; then
		#statements
		package=$1
		loops=$2
	fi

	if [[ -n package ]]; then
		adb shell monkey -p ${package} -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
	else
		echo "Please start the app and make sure it is the top activity."
	fi

	#statements
	dump_window=`adb shell dumpsys window |grep mFocusedWindow`
	OLD_IFS="$IFS"
	IFS=" "
	# remove "mFocusedWindow=Window{"
	array=(${dump_window#*{}})
	IFS="$OLD_IFS"

	active_window=${array[2]}
	package=${active_window%/*}

	activity=${active_window#*/}
	activity=${activity%%\}*}

}