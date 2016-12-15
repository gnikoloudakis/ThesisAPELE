from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

jobstores = {
    # 'mongo': MongoDBJobStore(database='mongostore',collection='mongojobs',),
    # 'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
    'default': MemoryJobStore()
}
executors = {
    'default': ThreadPoolExecutor(5),
    'processpool': ProcessPoolExecutor(3)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
