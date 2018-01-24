from django.db import models

# Create your models here.

from django.utils import timezone

# Extending User Model Using a One-To-One Link
# From: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone

from django.contrib.auth.models import User, Group
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
"""

class Location(models.Model):
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.location

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, blank=True)
    location = models.ForeignKey(Location, related_name='Location')
    #location = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    manager = models.ForeignKey(User, related_name='Manager', default=1)
    #manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Mgr', default=0)

    def __str__(self):
        string = self.user.last_name + ", " + self.user.first_name
        #string = User.last_name + ", " + User.first_name
        return string
    """
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.userprofile.save()
    """
class Category(models.Model):
    category = models.CharField(max_length=200)

    def __str__(self):
        return self.category

class Unavailability(models.Model):
    unavailability = models.CharField(max_length=200)
    category = models.ForeignKey(Category, related_name='Category')

    def __str__(self):
        return self.unavailability

class Register(models.Model):
    user = models.ForeignKey(User, related_name='User')
    unavailability = models.ForeignKey(Unavailability, related_name='Unavailability')
    hours = models.FloatField()
    comments = models.CharField(max_length=41, blank=True)
    start_date = models.DateField(default=timezone.now)
    #end_date = models.DateField(default=timezone.now)
    created_date = models.DateTimeField(default=timezone.now)

    def get_start_year(self):
        return self.start_date.year

    def __str__(self):
        string = "ID=" + str(self.id) + ", " + self.user.last_name + ", " + self.user.first_name + ": " + self.start_date.strftime("%Y-%m-%d, %I:%M ")
        return string
