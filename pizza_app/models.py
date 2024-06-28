from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Items(models.Model):
    
    all_food_types = (
        ('Non-Veg', 'Non-Veg'),
        ('Veg', 'Veg')
    )

    category = models.CharField(max_length = 30)
    food_name = models.CharField(max_length = 50)
    prize = models.IntegerField()
    image = models.ImageField(upload_to='food_images/')
    food_type = models.CharField(max_length = 30, choices = all_food_types)
    description = models.TextField()
    

    def __str__(self):
        return f"{self.id} | {self.food_name} | {self.category} | {self.prize}"


class ContactMessages(models.Model):
    name = models.CharField(max_length = 50)
    email = models.EmailField(max_length=50)
    subject = models.CharField(max_length = 300)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} | {self.email}"
    

# This is a Single Cart Object.
class CartItem(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Items, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} | {self.item.food_name}"
    

# This is the final Order Object that is created after the user proceeds for checkout.
class OrderObject(models.Model):
    
    ORDER_STATUS = (
                        ('PENDING', 'PENDING'),
                        ('OUT-FOR-DELIVERY', 'OUT-FOR-DELIVERY'),
                        ('DELIVERED', 'DELIVERED')
                    )

    DELIVERY_TYPES = (
                        ('Express-Delivery', 'Express-Delivery'),
                        ('Standard-Delivery', 'Standard-Delivery'),
                    )

    user = models.ForeignKey(User, on_delete = models.CASCADE)
    item_count = models.IntegerField()
    all_items_ordered = models.BinaryField()
    
    delivery_category = models.CharField(max_length = 50, choices=DELIVERY_TYPES, default="Standard-Delivery")
    delivery_charge = models.IntegerField(default=100)

    total_price = models.IntegerField()
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default="PENDING")
    is_paid = models.BooleanField(default=False)    


    def __str__(self):
        return f"{self.user} | {self.order_status}"



class saved_card(models.Model):
    card_number = models.CharField(max_length=20)
    card_date = models.CharField(max_length=5)
    user_name = models.CharField(max_length=30)
    card_provider = models.CharField(max_length=10)
    card_cvv = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.card_number}"
