from django.db import models
from django.utils import timezone

from cabinet.models import CustomUser


class Transaction(models.Model):
    psychologist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="transactions")
    client = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2) # positalk fee
    service_fee = models.DecimalField(max_digits=10, decimal_places=2) # acquiring fee
    net_amount = models.DecimalField(max_digits=10, decimal_places=2) # for psychologist
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("completed", "Completed")])

    def save(self, *args, **kwargs):
        # Рассчет чистого дохода
        self.net_amount = self.amount - self.commission - self.service_fee
        super().save(*args, **kwargs)


class PayoutRequest(models.Model):
    psychologist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="payout_requests")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")])
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def approve(self):
        if self.psychologist.balance >= self.amount:
            self.psychologist.balance -= self.amount
            self.psychologist.save()
            self.status = "approved"
            self.processed_at = timezone.now()
            self.save()
        else:
            raise ValueError("Insufficient balance")

    def reject(self):
        self.status = "rejected"
        self.save()