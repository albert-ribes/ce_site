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
    manager = models.ForeignKey(User, related_name='LocManager', blank=True, default=6)
    def __str__(self):
        string=self.location + ", manager=" + str(self.manager.first_name) + " " + str(self.manager.last_name)
        return string

class KindOfDay(models.Model):
    kindofday = models.CharField(max_length=20, blank=True)
    comment = models.CharField(max_length=41, blank=True)
    laborablehours = models.FloatField()
    def __str__(self):
        return self.kindofday

class CalendarEvent(models.Model):
    location = models.ForeignKey(Location, related_name='Loc')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    kindofday = models.ForeignKey(KindOfDay, related_name='KindOfDay')
    comment = models.CharField(max_length=80, blank=True)
    def __str__(self):
        string = "ID=" + str(self.id) + "; " + self.start_date.strftime("%Y-%m-%d") + " - " + self.end_date.strftime("%Y-%m-%d") + ", " + self.location.location + ", " + self.kindofday.kindofday + "  -  " + self.comment
        return string

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
    short_name = models.CharField(max_length=80, blank=True, null=True, default=" ")
    def __str__(self):
        return self.category

class Unavailability(models.Model):
    unavailability = models.CharField(max_length=200)
    category = models.ForeignKey(Category, related_name='Category')

    def __str__(self):
        string = self.unavailability + " (" + str(self.category) + ")"
        return string

class Register(models.Model):
    user = models.ForeignKey(User, related_name='User')
    unavailability = models.ForeignKey(Unavailability, related_name='Unavailability')
    hours = models.FloatField(blank=True)
    comments = models.CharField(max_length=41, blank=True)
    date = models.DateField(default=timezone.now)
    #end_date = models.DateField(default=timezone.now)
    created_date = models.DateTimeField(default=timezone.now)
    createdby = models.ForeignKey(User, related_name='CreatedByUser')

    def get_start_year(self):
        return self.date.year

    def __str__(self):
        string = "ID=" + str(self.id) + ", " + self.user.last_name + ", " + self.user.first_name + ": " + self.date.strftime("%Y-%m-%d, %I:%M ")
        return string

