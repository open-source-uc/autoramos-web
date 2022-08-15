from celery import shared_task
from datetime import datetime
from .backend import tomar_ramos, revalidar_cookies


@shared_task
def reserva_creada(mes, dia, horas, minutos):
    datetime_str = f'{dia}/{mes}/2022 {horas}:{minutos}:00'
    date_time_obj = datetime.strptime(datetime_str, '%d/%m/%y %H:%M:%S')

    return date_time_obj


@shared_task
def reservar(usuario):
    tomar_ramos(usuario)
    return None


@shared_task(name='revalidar_cookie')
def celery_revalidar_cookie():
    revalidar_cookies()
    return None
