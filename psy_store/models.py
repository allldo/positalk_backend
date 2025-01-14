from django.db.models import Model, PositiveIntegerField, CharField, TextField


class GiftSession(Model):
    quantity = PositiveIntegerField(default=1, null=False, blank=False, verbose_name="Количество")
    price = PositiveIntegerField(verbose_name="Цена")
    description = CharField(max_length=350, verbose_name="Описание")

    def __str__(self):
        return f"{self.id} gift with price {self.price} rubles"


# class Service(Model):
#     title = CharField()
#     description = TextField()
#     price = PositiveIntegerField()
#     duration = PositiveIntegerField()
