import json
import redis
from celery import Celery
from modules.mailing.services import MailingService
from random import randint


app = Celery("celery_", broker="redis://redis:6379")
app.autodiscover_tasks()


# таска запуска процесса
@app.task
def start_mailing(mailing_id: int):
    r = redis.Redis(host="redis")
    r.set(str(mailing_id), json.dumps({"status": "in_process"}))
    mailing_service = MailingService(mailing_id)
    mailing_service.start_mailing()
    r.set(str(mailing_id), json.dumps({"status": "finished"}))
