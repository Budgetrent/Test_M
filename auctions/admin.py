from django.contrib import admin
from .models import Category, Location, Property, Comment, User, Bid

# Register your models here.
admin.site.register(User)
admin.site.register(Location)
admin.site.register(Category)
admin.site.register(Property)
admin.site.register(Comment)
admin.site.register(Bid)
