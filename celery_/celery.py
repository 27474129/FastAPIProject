from celery import Celery
from modules.mailing.services import MailingService


"""
    Решил не использовать брокеры сообщений тк посчитал структуру тех же самых messages достаточно сложной, 
    чтобы использовать postgresql, плюс в рамках тестового задания не думаю что это принципиальный момент, хотя вероятно
    в коммерции я был бы не прав, особенно на высоконагруженном проекте
"""
app = Celery("celery_", broker="redis://redis:6379")
app.autodiscover_tasks()


# таска запуска процесса
@app.task
def start_mailing(mailing_id: int):
    mailing_service = MailingService(mailing_id)
    mailing_service.start_mailing()
