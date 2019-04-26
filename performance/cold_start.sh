#!/bin/bash

# @author: Gaochuang Yang
# @date: 04/12/2019
# @description:
# This is a script to record the cold-start time for an activity
# example:
# sh cold-start.sh package_name 20
# 第一个参数是package name，用于起应用的
# 第二个参数是循环多少次，用于最终统计平均时间的

loops=20 #default is 20

package=''
activity=''

source utils.sh

get_package $1

# set the loops from input, by default it is set to 20
if [[ $# -ge 2 ]]; then
    loops=$2
fi

#echo $package, $activity

if [ -n package ];then
	echo -e "Is \""$package"\" that your tested app or window? \n"
	echo -e "If not, please press control + c to terminate this process, then input the corrent package name and rerun the script.\n"
	echo -e "The results will be saved under folder \"results\", please check it. \n"
else
	echo "failed to dump the current window! or failed to get the current app name or activity, please exit."
	exit 1
fi

#create the test result file
timestamp=$(date "+%Y%m%d_%H%M")
#res="res/xg_start_"`get_timestamp.sh`".csv"
res="results/cold_start_"$package"_"$timestamp".csv"
touch $res
echo "" > ${res}

function cold_start {
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
}

cold_start

sed -i "" "s/: /,/g" ${res}

echo -e "\n"
echo -e $package "的冷起最终结果如下："
#awk -F : '{print $1, $2}' ${res}
awk -F , '{val=int($2); total+=val}END{print "总共冷起了" NR-1 "次，平均时间是:" total/(NR-1) " ms."}' ${res}


