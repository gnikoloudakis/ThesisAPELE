import os, psutil
from time import gmtime, strftime

class write_file(object):
    def __init__(self, path):
        # self.timestamp = time.time()
        self.pathf = path

    def startFile(self):
        with open(self.pathf + '/logs/log.txt', 'a') as logfile:
            logfile.write('---------------------------------' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + '---------------------------' + '\n')

    def outputFile(self, text1, text2):
        with open(self.pathf + '/logs/log.txt', 'a') as logfile:
            logfile.write('CPU' + ',' + psutil.cpu_percent() + ',' + text1 + ',' + text2 + '\n')
