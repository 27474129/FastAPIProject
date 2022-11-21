import logging


logger = logging.getLogger(__name__)


# декоратор для обработки ошибок в views
def errors_handler(view):
    async def wrapper():
        try:
            return await view()
        except Exception as e:
            logger.error(e)
    return wrapper
