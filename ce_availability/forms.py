from django import forms
from django.forms import ModelForm, DateTimeInput, DateInput
from .models import Register, Employee, Unavailability, CalendarEvent, Category, Location, KindOfDay
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from django.contrib.admin.widgets import AdminDateWidget
from django.utils import timezone

from django.contrib.admin import widgets

class RegisterForm(forms.ModelForm):
    unavailability = forms.ModelChoiceField(queryset=Unavailability.objects.order_by('unavailability'))
    register_id=0
    user=0
    hidden_type_date_input = forms.CharField(initial= "single_date")
    start_date = forms.DateField(initial=date.today, widget=DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(initial=date.today, widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        currentYear = datetime.now().year
        YEAR_CHOICES =  (str(currentYear+1),str(currentYear),str(currentYear-1),str(currentYear-2))
        model = Register
        fields = ('user', 'unavailability', 'hours', 'date','comments',)
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, user, register_id, ce_choices, *args, **kwargs):
       super(RegisterForm, self).__init__(*args, **kwargs)
       self.fields['user'].choices = ce_choices
       self.register_id=register_id
       self.user=user
       self.fields['date'].required = False
       self.fields['start_date'].required = False
       self.fields['end_date'].required = False
       self.fields['hidden_type_date_input'].required = False
       #print ("INFO: FORMS.RegisterForm.__init__, register_id=" + str(register_id))

    def clean(self):
        #print("RegisterForm: CLEAN")
        try:
           date=self.cleaned_data.get('date')
        except:
           print("Oops!  That was no valid date.  Try again...")
        hours=self.cleaned_data.get('hours')
        type_date_input = self.cleaned_data.get('hidden_type_date_input')
        if(type_date_input==""):
            type_date_input = "single_date"
        ce=self.cleaned_data.get('user') 
        user = User.objects.filter(id=self.user.id).get()
        #print(type_date_input)
        if(type_date_input=="single_date"):
            
            location_id=Employee.objects.filter(user_id=self.user.id).values_list('location', flat=True).get()
            calendar_events=CalendarEvent.objects.filter(start_date__lte=date).filter(end_date__gte=date).filter(location=location_id).order_by('start_date')
            #print(calendar_events)
            #print(user)
            #hours = float(hours)
            #hours=float(str(hours).replace(',',''))
            kindofday=""
            if(date and date!=None):
                dayofweek=date.weekday()
                calendar_events = CalendarEvent.objects.filter(start_date__lte=date).filter(end_date__gte=date).filter(location=user.employee.location).order_by('start_date')
                for event in calendar_events:
                     #print(event)
                     delta = event.end_date - event.start_date
                     for i in range(delta.days +1):
                        day_event=event.start_date + timedelta(days=i)
                        #print(str(day.year) + "-"+ str(day.month) + "-" + str(day.day) + ", weekday=" + str(day.weekday()))
                        if(date==day_event):
                            print("Day: " + str(day_event) + ", " + str(event.kindofday))
                            kindofday=str(event.kindofday)
                            print("Day: " + str(day_event) + ", " + kindofday)
            
                ce=self.cleaned_data.get('user')
                register_id=self.register_id
                """
                if hours:
                    print("INFO: FORMS.RegisterForm.clean, start_date:" + str(start_date) + ", hours=" + str(hours) + ", ce=" + str(ce) + ", register_id=" + str(register_id))
                """
                registers = Register.objects.filter(date=date).filter(user__username=ce)
                sum_hours=0
                for register in registers:
                    sum_hours=sum_hours+register.hours
                if (register_id!=0):
                    sum_hours=sum_hours - Register.objects.filter(id=register_id).values_list('hours', flat=True).get()
                
                print ("INFO: FORMS.RegisterForm.clean, user= " + str(ce) + ", dayofweek=" + str(dayofweek) + ", inserted_hours=" + str(hours) + ", sum_hours=" + str(sum_hours))

                if hours==None:
                    raise forms.ValidationError({'hours': ["This field is required.",]})
                if hours!=None:
                    if(kindofday=="Festive"):
                        raise forms.ValidationError({'hours': ["No unavailabilities allowed during festives.",]})
                    if (hours<=0.0):
                       raise forms.ValidationError({'hours': ["Value must be greater than 0.",]})
                    if (dayofweek==4):
                        if (sum_hours + hours > 7):
                            raise forms.ValidationError({'hours': ["The total amount of unavailable hours cannot be greather than 7 in that day.",]})
                    if (dayofweek==5 or dayofweek==6.0):
                        raise forms.ValidationError({'date': ["No unavailabilities allowed during the weekend.",]})
                    if(kindofday=="Intensive"):
                        if (sum_hours + hours > 7):
                            raise forms.ValidationError({'hours': ["The total amount of unavailable hours cannot be greather than 7 in that day.",]})
                    if (dayofweek>=0 and dayofweek<=3):
                        if (sum_hours + hours > 8.5):
                            raise forms.ValidationError({'hours': ["The total amount of unavailable hours cannot be greather than 8,5 in that day.",]})
            else:
                raise forms.ValidationError({'date': ["",]})
                print("Invalid Date")
        elif(type_date_input=="range_date"):
            #convertir les dates en rang
            #comprovar que no hi ha esdeveniments
            #comprovar tipus de dia (de la setmana/jornada intensiva)
            #introduir el registre que toqui per cada dia
            start_date = self.cleaned_data.get('start_date')
            end_date = self.cleaned_data.get('end_date')
            if(start_date>=end_date):
                raise forms.ValidationError({'start_date': ["The Start Date cannot be the same or older than the End Date.",]})
            delta_range = end_date - start_date
            registers = Register.objects.filter(date__gte=start_date).filter(date__lte=end_date).filter(user__username=ce)
            if registers:
                raise forms.ValidationError({'start_date': ["There are already unavailabilities during this range of dates.",]})

class ListFilterForm(forms.Form):
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    currentWeek = datetime.now().isocalendar()[1]
    firstDayWeek = datetime.now() - timedelta(days=datetime.now().weekday())
    lastDayWeek = firstDayWeek + timedelta(days=6)
    #print("INFO: ListFilterForm, " + currentYear + "," + currentMonth)
    
    YEAR_CHOICES =  (('All','  All'),(str(currentYear+1),str(currentYear+1)), (str(currentYear),str(currentYear)),(str(currentYear-1),str(currentYear-1)),(str(currentYear-2),str(currentYear-2)))
    MONTH_CHOICES = (('All','  All'),('1','January'), ('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','Desember'))
    WEEK_CHOICES = (('All', '  All'),(currentWeek,'Current'))
    #Filter selectors
    ce_selector = forms.ChoiceField(label='CE', choices=[(choice.pk, choice.last_name + ", " + choice.first_name) for choice in User.objects.filter(groups__name='CE').order_by('last_name')])
    """
    for choice in Unavailability.objects.all():
        print(choice)
    """
    unavailability_selector = forms.ChoiceField(label='Unavailability', choices=[(choice.pk, choice) for choice in Unavailability.objects.all().order_by('unavailability')])
    #category_selector = forms.ChoiceField(label='Category', choices=[(choice.pk, choice) for choice in Category.objects.all().order_by('category')])
    category_selector = forms.ChoiceField(label='Category', choices=[(choice.pk, choice) for choice in Category.objects.all().order_by('category')])
    #unavailability_selector = forms.ChoiceField(label='Unavailability', choices=[(choice.pk, choice) for choice in Unavailability.objects.values_list('unavailability').distinct()])
    year_selector = forms.ChoiceField(label='Year',choices=YEAR_CHOICES)
    month_selector = forms.ChoiceField(label='Month',choices=MONTH_CHOICES)
    week_selector = forms.ChoiceField(label='Week',choices=WEEK_CHOICES)
    

    def __init__(self, user, ce_choices, *args, **kwargs):
       super(ListFilterForm, self).__init__(*args, **kwargs)
       self.fields['ce_selector'].choices = ce_choices
       #self.fields['ce_selector'].choices = [('All', 'All')] + list(self.fields['ce_selector'].choices)
       self.fields['unavailability_selector'].choices = [('All', 'All')] + list(self.fields['unavailability_selector'].choices)
       self.fields['category_selector'].choices = [('All', 'All')] + list(self.fields['category_selector'].choices)

    def save(self, commit=True):
        #print("> INFO, forms.py: save() method")
        year = self.cleaned_data.get('year_selector', None)
        month = self.cleaned_data.get('month_selector', None)
        ce = self.cleaned_data.get('ce_selector', None)
        unavailability = self.cleaned_data.get('unavailability_selector', None)
        category = self.cleaned_data.get('category_selector', None)
        week =  self.cleaned_data.get('week_selector', None)
        #print("INFO: FORMS.ListFilterForm.save " + ce + ", " + unavailability + ", " +  category + ", " + year + ", " + month + ", " + week)
        return(ce, unavailability, category, year, month, week)

    def clean_ce_selector(self):
        #print ("INFO: FORMS.ListFilterForm.clean, ")
        data = self.cleaned_data.get('ce_selector')
        data = self.cleaned_data['ce_selector']
        #print("INFO: FORMS.ListFilterForm.clean, " + str(data))
        return data

class CalendarFilterForm(forms.Form):
    currentMonth = datetime.now().month
    currentYear = datetime.now().year

    YEAR_CHOICES =  ((str(currentYear+1),str(currentYear+1)), (str(currentYear),str(currentYear)),(str(currentYear-1),str(currentYear-1)),(str(currentYear-2),str(currentYear-2)))
    MONTH_CHOICES = (('1','January'), ('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','Desember'))
    MODE_CHOICES = (('hours','  Hours'),('percentage','Percentage'))

    year_selector = forms.ChoiceField(label='Year',choices=YEAR_CHOICES)
    month_selector = forms.ChoiceField(label='Month',choices=MONTH_CHOICES)
    mode_selector = forms.ChoiceField(label='Year',choices=MODE_CHOICES)

    def save(self, commit=True):
        #print("> INFO, forms.py: save() method")
        year = self.cleaned_data.get('year_selector', None)
        month = self.cleaned_data.get('month_selector', None)
        mode = self.cleaned_data.get('mode_selector', None)
        #print("INFO: FORMS.ListFilterForm.save " + mode + ", " + year + ", " + month)
        return(mode, year, month)

class CalendarEventFilterForm(forms.Form):

    location_selector = forms.ChoiceField(label='Location', choices=[(choice.pk, choice) for choice in Location.objects.all().order_by('location')])
    kindofday_selector = forms.ChoiceField(label='KindOfDay', choices=[(choice.pk, choice) for choice in KindOfDay.objects.all().order_by('kindofday')])

    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    YEAR_CHOICES =  ((str(currentYear+1),str(currentYear+1)), (str(currentYear),str(currentYear)),(str(currentYear-1),str(currentYear-1)),(str(currentYear-2),str(currentYear-2)))
    MONTH_CHOICES = (('All', 'All'), ('1','January'), ('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','Desember'))
    year_selector = forms.ChoiceField(label='Year',choices=YEAR_CHOICES)
    month_selector = forms.ChoiceField(label='Month',choices=MONTH_CHOICES)

    def __init__(self, user, location_choices, *args, **kwargs):
       super(CalendarEventFilterForm, self).__init__(*args, **kwargs)
       self.fields['location_selector'].choices = location_choices
       self.fields['kindofday_selector'].choices = [('All', 'All')] + list(self.fields['kindofday_selector'].choices)

    class Meta:
        model = CalendarEvent

    def save(self, commit=True):
        #print("> INFO, forms.py: save() method")
        year = self.cleaned_data.get('year_selector', None)
        month = self.cleaned_data.get('month_selector', None)
        location = self.cleaned_data.get('location_selector', None)
        kindofday = self.cleaned_data.get('kindofday_selector', None)
        #print("INFO: FORMS.CalendarEventFilterForm.save " + location + ", " + ", " + kindofday + ", " + year + ", " + month)
        return(location, kindofday, year, month)


class CalendarEventForm(forms.ModelForm):
    #location_selector = forms.ChoiceField(label='Location', choices=[(choice.pk, choice) for choice in Location.objects.all().order_by('location')])

    class Meta:
        model = CalendarEvent
        fields = ('location', 'kindofday', 'start_date', 'end_date','comment')

        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, user, location_choices, *args, **kwargs):
       super(CalendarEventForm, self).__init__(*args, **kwargs)
       self.fields['location'].choices = location_choices
       self.user=user
       #print ("INFO: FORMS.CalendarEventForm.__init__, event_id=" + str(event_id))


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        #fields = ('employee_id', 'phone', 'location')
        fields = ('employee_id', 'phone')
