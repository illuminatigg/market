import datetime
import os
import time

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()
# ______________________________________________________________________________________________________________________
import asyncio

import pandas as pd
from openpyxl import Workbook
from config.settings import MEDIA_ROOT

from market.models import Schedule, Order, EndMessage
from config.settings import BOT


def work_time_end() -> bool:
    schedule = Schedule.objects.first()
    time = datetime.datetime.now().time()
    if time >= schedule.end_time:
        return True
    else:
        return False


async def send_end_message(user):
    msg = EndMessage.objects.first()
    message = msg.text
    await BOT.send_message(user, text=message)


def main():
    while True:
        market_closed = work_time_end()
        if market_closed:
            try:
                orders = Order.objects.filter(status='opened').update(status='created')
                for order in orders:
                    asyncio.run(send_end_message(order.owner))
                time.sleep(43200)
            except Exception as ex:
                print(ex)
        else:
            print('!!!!!!!!!!!!!!! work not ended')
            time.sleep(10)
            continue
