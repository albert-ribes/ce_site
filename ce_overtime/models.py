from django.db import models

from django.utils import timezone
from ce_availability.models import Employee
from django.contrib.auth.models import User, Group

# Create your models here.

class Category(models.Model):
    category = models.CharField(max_length=200)
    short_name = models.CharField(max_length=80, blank=True, null=True, default=" ")

    def __str__(self):
        return self.category

class Overtime(models.Model):
    overtime = models.CharField(max_length=200)
    category = models.ForeignKey(Category, related_name='Category')

    def __str__(self):
        string = self.unavailability + " (" + str(self.category) + ")"
        return string


class RegisterOvertime(models.Model):
    usr = models.ForeignKey(User, related_name='usr')
    overtime = models.ForeignKey(Overtime, related_name='Overtime')
    travel_hours = models.FloatField(blank=True)
    work_hours = models.FloatField(blank=True)
    others_hours = models.FloatField(blank=True)
    comments = models.CharField(max_length=41, blank=True)
    date = models.DateField(default=timezone.now)
    #end_date = models.DateField(default=timezone.now)
    created_date = models.DateTimeField(default=timezone.now)
    createdbyuser = models.ForeignKey(User, related_name='createdbyuser')

    def get_start_year(self):
        return self.date.year

    def __str__(self):
        string = "ID=" + str(self.id) + ", " + self.user.last_name + ", " + self.user.first_name + ": " + self.date.strftime("%Y-%m-%d, %I:%M ")
        return string
