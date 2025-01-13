import hashlib
import hmac
import json
from datetime import datetime

import requests

# Секретный ключ
secret_key = "2958e2d7401d84018fa413cf1e221bc5e8a142d3cb159870ab561486a7540445"

# Данные для формирования ссылки
transaction_id = 123  # Уникальный идентификатор транзакции
customer_phone = "+79991234567"  # Телефон клиента
object_data = {
    "title": "Название товара",
    "id": 456,  # ID объекта
    "price": 1500.00,  # Цена объекта
}

data = {
    "do": "link",  # Тип действия
    "callbackType": "json",  # Тип обратного вызова
    "order_id": str(transaction_id),  # ID заказа
    "customer_phone": customer_phone,  # Телефон клиента
    "installments_disabled": "1",  # Отключение рассрочки
    "link_expired": datetime(2025, 1, 14, 11, 38).strftime("%Y-%m-%d %H:%M"),  # Срок действия ссылки
    "products[0][name]": object_data["title"],  # Название товара
    "products[0][sku]": str(object_data["id"]),  # SKU товара
    "products[0][price]": str(object_data["price"]),  # Цена товара
    "products[0][quantity]": "1",  # Количество
}
headers = {
    'Content-Type': 'text/plain',
    'charset': 'utf-8'
}

response = requests.get('https://demo.payform.ru/', params=data, headers=headers, timeout=5)

# Получение ответа
print(response.text)