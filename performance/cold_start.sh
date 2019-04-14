#!/bin/bash

# @author: Gaochuang Yang
# @date: 04/12/2019
# @description:
# This is a script to record the cold-start time for an activity
# example:
# sh cold-start.sh package_name 20
# 第一个参数是package name，用于起应用的
# 第二个参数是循环多少次，用于最终统计平均时间的

package=''
loops=20 #default is 20



if [[ $# -eq 0 ]]; then
	#statements
	echo "No arguments."
	echo "Usage: cold-start.sh package_name loops"
	echo "So if no package (the first argument), please start the tested app and make sure it is in the top. The script will capture \
		the current activity, then start to test."
	echo "So if no loop number， the default loop number is 20"
fi

if [[ $# -eq 1 ]]; then
	#statements
	package=$1
fi
if [[ $# -ge 2 ]]; then
	#statements
	package=$1
	loops=$2
fi

if [[ -n package ]]; then
	adb shell monkey -p ${package} -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
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

if [ -n package ];then
	echo "Is that your tested app or window? "$package
	echo "If not, please press control + c to terminate this process"
else
	echo "failed to dump the current window! exit."
fi

#echo $active_window
# Get the top activity window
activity=${active_window#*/}
activity=${activity%%\}*}
#echo ${activity}

#create the test result file
timestamp=$(date "+%Y%m%d_%H%M")
#res="res/xg_start_"`get_timestamp.sh`".csv"
res="results/cold_start_"$package"_"$timestamp".csv"
touch $res
echo "" > ${res}

#execute the loop
for((i=1; i<=$loops; i++));
do
adb shell am force-stop ${package}
sleep 5
# adb shell am kill com.ss.android.article.video
adb shell am start -W ${package}"/"${activity} | grep TotalTime >> ${res}
sleep 2
# 打印“.”的个数来表示循环次数，比如"..."表示第3次循环
#seq -s '.' $i |sed 's/[0-9]//g'
echo -e $i"\t\c"
done

sed -i "" "s/: /,/g" ${res}

echo -e "\n"
echo -e $package "的冷起最终结果如下："
#awk -F : '{print $1, $2}' ${res}
awk -F , '{val=int($2); total+=val}END{print "总共冷起了" NR-1 "次，平均时间是:" total/(NR-1) " ms."}' ${res}

