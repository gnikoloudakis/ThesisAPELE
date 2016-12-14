import os, time


class write_file(object):
    def __init__(self):
        self.timestamp = time.time()

    def outputFile(self, text1, text2):
        with open('../logs/log.txt', 'a') as logfile:
            logfile.write(text1 + ',' + text2 + '\n')
