import uuid
from datetime import timedelta
import requests
from django.utils.datetime_safe import datetime
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, CharField, DecimalField
from rest_framework.serializers import Serializer


class LinkPaymentSerializer(Serializer):
    customer_phone = CharField(max_length=15)
    title = CharField(max_length=255)
    object_id = IntegerField()
    price = DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data):
        link_expired_time = datetime.now() + timedelta(minutes=30)
        transaction_id = str(uuid.uuid4())
        data = {
            "do": "link",
            "callbackType": "json",
            "order_id": transaction_id,
            "customer_phone": validated_data["customer_phone"],
            "installments_disabled": "1",
            "link_expired": link_expired_time.strftime("%Y-%m-%d %H:%M"),
            "products[0][name]": validated_data["title"],
            "products[0][sku]": str(validated_data["object_id"]),
            "products[0][price]": str(validated_data["price"]),
            "products[0][quantity]": "1",
        }
        headers = {
            'Content-Type': 'text/plain',
            'charset': 'utf-8'
        }

        try:
            response = requests.get('https://demo.payform.ru/', params=data, headers=headers, timeout=5)
            return {"link": response.text, "link_expired_time": link_expired_time.strftime("%Y-%m-%d %H:%M")}
        except requests.RequestException as e:
            raise ValidationError(f"Ошибка при генерации ссылки: {str(e)}")