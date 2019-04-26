#!/usr/bin/env bash

total_frames=0
jank_frames=0
vsync_overtime=0
res="FPS_com.ss.android.article.news_20190425_1550.csv"

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
echo "total frames is : "$total_frames
echo "total jank frames is : "$jank_frames
echo "total vsync_overtime is : "$vsync_overtime