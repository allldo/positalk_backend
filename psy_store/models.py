from django.db.models import Model, PositiveIntegerField, CharField


class GiftSession(Model):
    quantity = PositiveIntegerField(default=1, null=False, blank=False)
    price = PositiveIntegerField()
    description = CharField(max_length=350)

    def __str__(self):
        return f"{self.id} gift with price {self.price} rubles"
