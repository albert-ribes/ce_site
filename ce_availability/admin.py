from django.contrib import admin

# Register your models here.
#from .models import CE
from .models import Unavailability
from .models import Register
from .models import Employee

#admin.site.register(CE)
admin.site.register(Unavailability)
admin.site.register(Register)
admin.site.register(Employee)

