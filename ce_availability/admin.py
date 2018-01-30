from django.contrib import admin

# Register your models here.
#from .models import CE
from .models import Unavailability
from .models import Register
from .models import Employee
from .models import Category
from .models import Location
from .models import KindOfDay
from .models import CalendarEvent

#admin.site.register(CE)
admin.site.register(Unavailability)
admin.site.register(Register)
admin.site.register(Employee)
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(KindOfDay)
admin.site.register(CalendarEvent)
