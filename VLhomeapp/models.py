from django.conf import settings
from django.db import models


class Restaurant(models.Model):
    """Restoran haqida umumiy ma'lumot (logo, nom, aloqa)"""
    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to="logo/", blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    """Menyu bo'limi (masalan: Ichimliklar, Salatlar, Asosiy taomlar)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="menus/", blank=True, null=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('preparing', 'Tayyorlanmoqda'),
        ('delivering', 'Yetkazilmoqda'),
        ('done', 'Yetkazildi'),
        ('cancelled', 'Bekor qilindi'),
    ]
    # ... boshqa maydonlar
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)


class Dish(models.Model):
    """Taom"""
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="dishes")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="dishes/", blank=True, null=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Dishes"

    def __str__(self):
        return f"{self.name} - {self.price}"


class Order(models.Model):
    """Buyurtma"""

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        PREPARING = "preparing", "Tayyorlanmoqda"
        READY = "ready", "Tayyor"
        DELIVERED = "delivered", "Yetkazildi"
        CANCELLED = "cancelled", "Bekor qilindi"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    customer_name = models.CharField(max_length=100, blank=True)
    table_number = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Buyurtma #{self.id} - {self.get_status_display()}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

class OrderItem(models.Model):
    """Buyurtmadagi bitta taom va uning soni"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    # bo'sh qoldirilsa, saqlashda taomning hozirgi narxi olinadi
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        if self.price is None:
            self.price = self.dish.price
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"