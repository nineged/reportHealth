# reportHealth
纺大健康码打卡

基于selenium的武汉纺织大学健康码自动打卡

crontab任务建议设置
0 1,2,3 * * * /bin/sh/root/reportHealth/main.sh >> /root/reportHealth/rh.py.log 2>&1
