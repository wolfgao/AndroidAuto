# AndroidAuto framework
This is an Android UI automation test framework, which integrated performance test (mainly using shell scripts), 
and UI test (UI crawler, Monkey, and  Instrumental test - ATX, adb wrapper, etc)

## project structure
:--- common: common class  
:--- Performance  
&ensp;&ensp;|--- Response: cold start, hot start responses  
&ensp;&ensp;|--- FPS: Frame per second    
&ensp;&ensp;|--- CPU: Top CPU, and CPU for tested app, process    
&ensp;&ensp;|--- MEM: memory usage (pss) for tested app, process  
&ensp;&ensp;|--- Net: Network performance for tested app, proecss   
&ensp;&ensp;|--- results: saved some temporary results, if using CI, please check with CM for formal path.  
:--- products: please put your product business scripts here, using PO mode  
:--- report: the final reports will be saved here  
:--- testplans: saved some test suits, test cases, etc  
:--- utils: some adb util helpers, etc  

## How to do?

## Example:
