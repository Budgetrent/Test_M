from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import datetime

def current_year():
    return datetime.date.today().year

def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)

class Category(models.Model):
    category_type = models.CharField(max_length=64)
    
    def __str__(self):
        return self.category_type

class Location(models.Model):
    city = models.CharField(max_length=64)
    street = models.CharField(max_length=64)
    province = models.CharField(max_length=64)
    
    def __str__(self):
        return f"{self.province}, {self.city}, {self.street}"
    
class User(AbstractUser):
    def __str__(self):
        return self.username

class Bid(models.Model):
    bid = models.IntegerField(default=0, validators=[MinValueValidator(1)])
    user = models.ForeignKey(User,blank=True, null=True, related_name="user_bid", on_delete=models.CASCADE )
    
    def __str__(self):
        return f"{self.user}: {self.bid}"



class Property(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, related_name="property_owner")
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=100)
    year = models.IntegerField(validators=[MinValueValidator(1000), max_value_current_year])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=False, null=False, related_name="property_type" )
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=False, null=False, related_name="town")
    price = models.ForeignKey(Bid,on_delete=models.CASCADE, related_name="first_bid")
    square_meters = models.IntegerField(validators=[MinValueValidator(1)])
    isActive = models.BooleanField(default=True)
    watchlist = models.ManyToManyField(User, null=True, blank=True, related_name="watch_list")
    photo = models.CharField(max_length=1000)
    
    def __str__(self):
        return f"{self.owner}: {self.name}, {self.location}"
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, related_name="user_comment")
    property_id = models.ForeignKey(Property, on_delete=models.CASCADE, blank=False, null=False, related_name="property_comment")
    comment = models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.user}: {self.property_id}"
    
    
