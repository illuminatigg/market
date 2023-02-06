import datetime
import os

import pandas as pd
from celery import Celery
from celery.schedules import crontab

from config.celery import app
from config.settings import MEDIA_ROOT
from market.models import Manufacturer, Product, ProductModification, ProductsUploadFile, Order, ReportFile


@app.task
def excel_to_db(path, file_id):
    data = pd.read_excel(io=path)
    for index, line in enumerate(data.itertuples()):
        man, created = Manufacturer.objects.get_or_create(name=line[2])
        prod, created = Product.objects.get_or_create(manufacturer=man, name=line[3])
        mod = ProductModification.objects.create(
            product=prod,
            specifications=line[4],
            price_rub=line[5],
            price_dollar=line[6],
            quantity=line[7]
        )
    file = ProductsUploadFile.objects.get(id=file_id)
    file.delete()
    os.remove(path)


def create_report_file(oder_id):
    fields = {
        'Товар': [],
        'Колличество': [],
        'Стоимость': [],
        'Общая сумма': [],
        'Дата создания заказа': [],
        'Номер заказа': []
    }
    orders = Order.objects.filter(identifier=oder_id).prefetch_related('cart', 'cart__products')
    file_name = f'накладная {datetime.date.today().strftime("%d-%m-%Y")}.xlsx'
    for order in orders:
        for index, prod in enumerate(order.cart.products.all()):
            fields['Товар'].append(prod.product.specifications)
            fields['Колличество'].append(prod.quantity)
            fields['Стоимость'].append(prod.price)
            fields['Общая сумма'].append(order.cart.total if index == 0 else ' ')
            fields['Дата создания заказа'].append(datetime.datetime.now() if index == 0 else ' ')
            fields['Номер заказа'].append(order.identifier if index == 0 else ' ')
    file_path = os.path.join(MEDIA_ROOT, file_name)
    dataframe = pd.DataFrame(fields)
    dataframe.to_excel(file_path, sheet_name=file_name, index=False)
    return file_path


# @app.task
# def send_report():
#     orders = Order.objects.filter(status='opened').update(status='created')
#     for order in orders:
