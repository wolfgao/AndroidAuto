# This is a common shell scripts for android adb, am, wms, etc.

password='0428'

function get_package() {
	if [[ $# -eq 1 ]]; then
		#statements
		package=$1
	else
	    echo "you didn't set the tested package, so will take the top activity as the tested package."
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

function get_phone_display(){
    phone_display=`adb shell dumpsys window displays| grep -A 1 "mDisplayId=0"| awk -F"=|x| " 'END{print $6" "$7}'`
    display_height=`echo $phone_display | awk -F " " '{print $1}'`
    display_width=`echo $phone_display | awk -F " " '{print $2}'`
    echo $phone_display
}

function get_HDMI(){
    HDMI=`adb shell dumpsys window displays| grep -A 1 "Display:"| awk '{if($1=="Display:")I=substr($2,12,length($2)-11);if(I+0>0&&substr($1,1,4)=="init")printf substr($1,6,length($1)-5)"x"substr($2,1,length($2)-3)"x"I"x"}'`
    echo $HDMI
}
#arg1- loops
#arg2- 0/phone 1/--ext-display；For some os, which supports extended display, like Huawei, or TNT.
#arg3- x1 such as 1/2
#arg4- y1
#arg5- x2
#arg6- y2
#arg7- swipe time
#arg1|arg2|arg3/arg4/arg5/arg6/arg7
function swipe(){
get_phone_display
local check=`echo $1|awk -F "|" '{printf $1}'`
if [ $check -gt 0 ];then
	local device=`echo $1| awk -F "|" '{printf $2}'`
	local PtoP=`echo $1|awk -F "|" '{printf $3}'`
	if [ $device -eq 0 ];then
		local screen_size=`echo $phone_display| sed 's/ /\//g'`
	elif [ $device -eq 1 ];then
		local screen_size=`echo "$HDMI"| sed 's/x/\//g'`
	fi
	local P=`echo $screen_size/$PtoP|awk -F "/" '{printf int($1*$3/$4)" "int($2*$5/$6)" "int($1*$7/$8)" "int($2*$9/$10)" "$11}'`
	local i=0
	while [ $i -lt $check ];do
		if [ $device -eq 0 ];then
			input swipe $P 1>/dev/null 2>&1
		elif [ $device -eq 1 ];then
			input --ext-display swipe $P 1>/dev/null 2>&1
		fi
		local i=$((i+1))
		sleep 1
	done
fi
}


function wakeup() {
  get_phone_display
  local x1=`echo 0.5 $display_height|awk '{print $1*$2}'`
  local x2=`echo 0.5 $display_height|awk '{print $1*$2}'`
  local y1=`echo 0.8 $display_width|awk '{print $1*$2}'`
  local y2=`echo 0.3 $display_width|awk '{print $1*$2}'`
  adb shell input keyevent KEYCODE_POWER
  adb shell input swipe $x1 $y1 $x2 $y2 1500 >/dev/null
  adb shell input text $password && adb shell input keyevent 66
}