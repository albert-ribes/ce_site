from django.contrib import admin

# Register your models here.
#from .models import CE
from .models import Unavailability
from .models import Register
from .models import Employee
from .models import Category
from .models import Location

#admin.site.register(CE)
admin.site.register(Unavailability)
admin.site.register(Register)
admin.site.register(Employee)
admin.site.register(Category)
admin.site.register(Location)

