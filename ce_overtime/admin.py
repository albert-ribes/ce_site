from django.contrib import admin

# Register your models here.

#from .models import CE

from .models import Category
from .models import Overtime
from .models import RegisterOvertime

#admin.site.register(CE)
admin.site.register(Category)
admin.site.register(Overtime)
admin.site.register(RegisterOvertime)
