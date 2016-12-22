import os, psutil
from time import gmtime, strftime


def startFile(path):
    with open(path + '/logs/log.txt', 'a') as logfile:
        logfile.write('---------------------------------' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + '---------------------------' + os.linesep)


def outputFile(path, text1, text2):
    with open(path + '/logs/log.txt', 'a') as logfile:
        logfile.write('CPU' + ',' + str(psutil.cpu_percent()) + ',' + text1 + ',' + text2 + os.linesep)
        # 'CPU' + ',' + psutil.cpu_percent() + ',' +
