from celery import Celery
from modules.mailing.services import MailingService


app = Celery("celery_", broker="redis://redis:6379")
app.autodiscover_tasks()


@app.task
def start_mailing(mailing_id: int):
    mailing_service = MailingService(mailing_id)
    mailing_service.start_mailing()
