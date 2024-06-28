from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Items)

admin.site.register(ContactMessages)

admin.site.register(CartItem)

admin.site.register(OrderObject)

admin.site.register(saved_card)