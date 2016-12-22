from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
import sys
import os


class schedulers(object):
    def __init__(self, path):
        self.scheduler1 = BlockingScheduler()
        self.path = path
        print self.path
        # self.url = sys.argv[1] if len(sys.argv) > 1 else 'sqlite:///example.sqlite'
        self.url = r'sqlite:///'+self.path+'\example.sqlite'
        # self.url = sys.argv[1] if len(sys.argv) > 1 else 'sqlite:c:\\example.sqlite'
        self.scheduler1.add_jobstore('sqlalchemy', url=self.url)
        self.alarm_time = datetime.now() + timedelta(seconds=1)
