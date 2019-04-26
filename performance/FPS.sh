#!/usr/bin/env bash
# @author: Gaochuang Yang
# @date: 04/16/2019
# @description:
# This is a script to get FPS from a package
# example:

source ~/.bash_profile

#默认测试时间，以秒为单位
duration=10
package=''
activity=''

source utils.sh

get_package $1

echo $package

# set test duration from input, by default it is set to 10s
if [[ $# -ge 2 ]]; then
    duration=$2
fi

get_phone_display
echo $phone_display

display_height=`echo $phone_display | awk -F " " '{print $1}'`
display_width=`echo $phone_display | awk -F " " '{print $2}'`

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
res="results/FPS_"$package"_"$timestamp".csv"
touch $res

start_time=`date +%s`
let time_gap=$duration

#Android 6.0 以上这个命令提供了更多的绘制信息,可以得到整个包的绘制数据
function getGFX() {
    #echo $1
    echo "onDraw Prepare Execute" >> ${res}
    adb shell monkey -p $1 -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
    local x1=`echo 0.5 $display_height|awk '{print $1*$2}'`
    local x2=`echo 0.5 $display_height|awk '{print $1*$2}'`
    local y1=`echo 0.2 $display_width|awk '{print $1*$2}'`
    local y2=`echo 0.8 $display_width|awk '{print $1*$2}'`
    while [ $time_gap -gt 0 ]
    do
        #在获取新的数值前，需要操作屏幕产生数据，如果要测试的应用不需要这个动作就可以产生数据，可以注释掉这句话
        adb shell input swipe $x1 $y1 $x2 $y2 1500 >/dev/null
        adb shell dumpsys gfxinfo $1 framestats reset |awk -F ' ' '/^\t[0-9]*\.[0-9]/{print $1,$2,$3}' >> ${res}
        sleep 2
        current_time=`date +%s`
        let run_time=$current_time-$start_time
        echo $run_time
        let time_gap=$2-$run_time
    done
}

getGFX $package $duration

function get_FPS() {
    total_frames=0
    jank_frames=0
    fps=0

    while read line
    jank_total=''
    do
        if [ $total_frames -gt 0 ]; then
            jank_total=$(echo $line | awk -F ' ' -v janks=$jank_frames -v vsync_ot=$vsync_overtime 'BEGIN {sum=0}
            {sum=($1+$2+$3);if(sum>16.67){janks+=1}if(sum%16.67==0){vsync_ot+=int(sum/16.67)-1}else{vsync_ot+=int(sum/16.67)}}
            END {print janks, vsync_ot}')
            jank_frames=$(echo $jank_total | awk -F ' ' '{print $1}')
            vsync_overtime=$(echo $jank_total | awk -F ' ' '{print $2}')
        fi
        if [ ! -n "$line" ]; then
            break
        fi
        let total_frames=$total_frames+1
        let jank_framese+=1
        #let vsync_overtime+=1

    done < $res

    let total_frames=$total_frames-1

    #计算fps
    if [ $total_frames -gt 0 ]; then
        fps=$(echo $total_frames $vsync_overtime | awk '{print $1*60/($1+$2)}')
    fi

    echo "total frames is : "$total_frames
    echo "total jank frames is : "$jank_frames
    echo "total vsync_overtime is : "$vsync_overtime
    echo "FPS is: "$fps
}

get_FPS $res


#另外一种计算FPS的方式
#TODO：调试中。。。
function getFPS_bySurface(){
    local KPI=100
    echo "FU(s),LU(s),Date:$1,FPS:$2,Frames,jank,jank2,MFS(ms),OKT:$KPI,SS(%),WN" >${res}
    local uptime=`awk -v T="$EPOCHREALTIME" 'NR==3{printf("%.6f",T-$3/1000000000+8*3600)}' /proc/timer_list`
    while [ $time_gap -gt 0 ]
        do
        dumpsys SurfaceFlinger --latency-clear
        sleep 2
        dumpsys SurfaceFlinger --latency "$1"|awk -v time=$uptime -v target=$2 -v kpi=$KPI '{if(NR==1){r=$1/1000000;if(r<0)r=$1/1000;b=0;n=0;w=1}
        else{if(n>0&&$0=="")O=1;if(NF==3&&$2!=0&&$2!=9223372036854775807){x=($3-$1)/1000000/r;if(b==0)
        {b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};
        if(x>2)D+=1;m=r;o=0}else{c=($2-b)/1000000;if(c>500){O=1}else{n+=1;if(c>=r){C+=c;if(c>kpi)o+=1;
        if(c>=m)m=c;if(x>1)d+=1;if(x>2)D+=1;b=$2}else{C+=r;b=sprintf("%.0f",b+r*1000000)}}};
        if(n==1)s=sprintf("%.3f",$2/1000000000)};
        if(n>0&&O==1){O=0;if(n==1)t=sprintf("%.3f",s+C/1000);
        else t=sprintf("%.3f",b/1000000000);T=strftime("%F %T",time+t);f=sprintf("%.2f",n*1000/C);m=sprintf("%.0f",m);g=f/target;
        if(g>1)g=1;h=kpi/m;if(h>1)h=1;e=sprintf("%.2f",g*60+h*20+(1-o/n)*20);print s","t","T","f+0","n","d","D","m","o","e","w;n=0;
        if($0==""){b=0;w+=1}else{b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;
        if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}}}}' >>${res}

        current_time=`date +%s`
        let run_time=$current_time-$start_time
        echo $run_time
        let time_gap=$duration-$run_time
    done
}

#getFPS_bySurface $activity 60 &



