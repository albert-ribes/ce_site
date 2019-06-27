from django import forms
from .models import Register, Employee, Unavailability, CalendarEvent, Category, KindOfDay, Location
from django.forms import ModelForm, DateTimeInput, DateInput
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from django.contrib.admin.widgets import AdminDateWidget
from django.utils import timezone
from django.contrib.admin import widgets


currentMonth = datetime.now().month
currentYear = datetime.now().year
currentWeek = datetime.now().isocalendar()[1]

#LOCATION_CHOICES=[(choice.pk, choice) for choice in Location.objects.all().order_by('location')]
LOCATION_CHOICES=[('','---------')]
YEAR_CHOICES =  ((str(currentYear+1),str(currentYear+1)), (str(currentYear),str(currentYear)),(str(currentYear-1),str(currentYear-1)),(str(currentYear-2),str(currentYear-2)))
MONTH_CHOICES = (('1','January'), ('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','Desember'))
MODE_CHOICES = (('hours','  Hours'),('percentage','Percentage'))
WEEK_CHOICES = (('All', '  All'),(currentWeek,'Current'))

HoursIntensiveKindOfDay = KindOfDay.objects.filter(kindofday="Intensive").values_list('laborablehours', flat=True).get()
HoursLaborableKindOfDay = KindOfDay.objects.filter(kindofday="WorkingDay").values_list('laborablehours', flat=True).get()


class RegisterForm(forms.ModelForm):
    unavailability = forms.ModelChoiceField(queryset=Unavailability.objects.order_by('unavailability'))
    register_id=0
    user=0
    hidden_type_date_input = forms.CharField(initial= "single_date")
    hidden_type_hours_input = forms.CharField(initial= "insert")
    start_date = forms.DateField(initial=date.today, widget=DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(initial=date.today, widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        currentYear = datetime.now().year
        #YEAR_CHOICES =  (str(currentYear+1),str(currentYear),str(currentYear-1),str(currentYear-2))
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
       self.fields['hidden_type_hours_input'].required = False
       #print ("INFO: FORMS.RegisterForm.__init__, register_id=" + str(register_id))

    def clean(self):
        #print("RegisterForm: CLEAN")
        try:
           date=self.cleaned_data.get('date')
        except:
           print("Oops!  That was no valid date.  Try again...")
        type_date_input = self.cleaned_data.get('hidden_type_date_input')
        type_hours_input = self.cleaned_data.get('hidden_type_hours_input')
        if (type_hours_input == "insert"):
            hours=self.cleaned_data.get('hours')
        """
        if(type_date_input==""):
            type_date_input = "single_date"
        if(type_whole_day_input==""):
            type_whole_day_input = "hours"
        """
        ce=self.cleaned_data.get('user') 
        user = User.objects.filter(id=self.user.id).get()
        """
        unavailability = self.cleaned_data.get('unavailability') 
        if unavailability==None:
            raise forms.ValidationError({'unavailability': ["This field is required.",]})
        """
        #print("-- type_date_input: " + type_date_input + ", type_hours_input: " + type_hours_input)
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
                            #print("Day: " + str(day_event) + ", " + str(event.kindofday))
                            kindofday=str(event.kindofday)
                            #print("Day: " + str(day_event) + ", " + kindofday)
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
                    #print("sum_hours: " + sum_hours)
                #print ("INFO: FORMS.RegisterForm.clean, user= " + str(ce) + ", dayofweek=" + str(dayofweek) + ", inserted_hours=" + str(hours) + ", sum_hours=" + str(sum_hours))
                #print ("INFO: FORMS.RegisterForm.clean, type_whole_day_input=" + type_whole_day_input)
                if(type_hours_input=="insert"):
                    #print("type_hours_input==insert")
                    if hours==None:
                        raise forms.ValidationError({'hours': ["This field is required.",]})
                    if hours!=None:
                        if(kindofday=="Festive"):
                            raise forms.ValidationError({'hours': ["No unavailabilities allowed during festives.",]})
                        if (hours<=0.0):
                           raise forms.ValidationError({'hours': ["Value must be greater than 0.",]})
                        if (dayofweek==4):
                            if (sum_hours + hours > HoursIntensiveKindOfDay):
                                raise forms.ValidationError({'hours': ["The total amount of unavailable hours cannot be greather than "+str(HoursIntensiveKindOfDay)+"h.",]})
                        if (dayofweek==5 or dayofweek==6.0):
                            raise forms.ValidationError({'date': ["No unavailabilities allowed during the weekend.",]})
                        if(kindofday=="Intensive"):
                            if (sum_hours + hours > HoursIntensiveKindOfDay):
                                raise forms.ValidationError({'hours': ["The total amount of unavailable hours cannot be greather than "+str(HoursIntensiveKindOfDay)+"h.",]})
                        if (dayofweek>=0 and dayofweek<=3):
                            if (sum_hours + hours > HoursLaborableKindOfDay):
                                raise forms.ValidationError({'hours': ["The total amount of unavailable hours cannot be greather than "+str(HoursLaborableKindOfDay)+"h.",]})
                elif (type_hours_input=="whole_day"):
                    if(kindofday=="Festive"):
                        raise forms.ValidationError({'hours': ["No unavailabilities allowed during festives.",]})
                    if (dayofweek==5 or dayofweek==6.0):
                        raise forms.ValidationError({'date': ["No unavailabilities allowed during the weekend.",]})
                    if (dayofweek>=0 and dayofweek<=4 and sum_hours >0):
                        raise forms.ValidationError({'hours': ["There are already unavailabilities at that day.",]})
                    if (dayofweek>=0 and dayofweek<=3):
                        self.fields['hours'] = HoursLaborableKindOfDay
                    if (dayofweek==4):
                        self.fields['hours'] = HoursIntensiveKindOfDay
                    if(kindofday=="Intensive"):
                        self.fields['hours'] = HoursIntensiveKindOfDay
            else:
                raise forms.ValidationError({'date': ["",]})
                #print("Invalid Date")
        elif(type_date_input=="range_date"):
            #convertir les dates en rang
            #comprovar que no hi ha esdeveniments
            #comprovar tipus de dia (de la setmana/jornada intensiva)
            #introduir el registre que toqui per cada dia
            start_date = self.cleaned_data.get('start_date')
            if start_date==None:
                raise forms.ValidationError({'start_date': ["This field is required.",]})
            end_date = self.cleaned_data.get('end_date')
            if end_date==None:
                raise forms.ValidationError({'end_date': ["This field is required.",]})
            delta_range = end_date - start_date
            if(type_hours_input=="insert"):
                #print("type_hours_input==insert")
                if hours==None:
                    raise forms.ValidationError({'hours': ["This field is required.",]})
            if(type_hours_input=="insert"):
                if(start_date>=end_date):
                    raise forms.ValidationError({'start_date': ["The Start Date cannot be the same or older than the End Date.",]})
                if (type_hours_input == "insert"):
                    hours=self.cleaned_data.get('hours')
                calendar_events = CalendarEvent.objects.filter(start_date__lte=end_date).filter(end_date__gte=start_date).filter(location=user.employee.location).order_by('start_date')
                for i in range(delta_range.days + 1):
                    day_range = start_date + timedelta(days=i)
                    dayofweek=day_range.weekday()
                    ce=self.cleaned_data.get('user')
                    #print("############ DAY=" + str(day_range) + ", dayofweek: " + str(dayofweek) + ", ce:" + str(ce))
                    registers = Register.objects.filter(date=day_range).filter(user__username=ce)
                    #print(registers)
                    sum_hours=0
                    for register in registers:
                        sum_hours=sum_hours+register.hours
                    register_id=self.register_id
                    if (register_id!=0):
                        sum_hours=sum_hours - Register.objects.filter(id=register_id).values_list('hours', flat=True).get()
                    #print("sum_hours: " + str(sum_hours))
                    day_with_event = "None"
                    if calendar_events:
                        for event in calendar_events:
                            #print(event)
                            delta_events = event.end_date - event.start_date
                            for j in range(delta_events.days + 1):
                                day_event = event.start_date + timedelta(days=j)
                                if (day_range==day_event):
                                    #print("-kindofday=" + str(event.kindofday))
                                    if(str(event.kindofday)=="Intensive"):
                                        day_with_event = "Intensive"
                                        #print("Intensive")
                                    elif(str(event.kindofday)=="Festive"):
                                        #print("Festive")
                                        day_with_event = "Festive"
                    if(day_with_event == "Intensive" and 0<=dayofweek<=3):
                        if (hours + sum_hours > HoursIntensiveKindOfDay):
                            #print("The sum of unavailable hours at " + str(day_range) + " is not allowed (>7h).")
                            raise forms.ValidationError({'hours': ["The sum of unavailable hours at " + str(day_range) + " is not allowed (>"+str(HoursIntensiveKindOfDay)+"h).",]})
                    elif(day_with_event!="Festive"):
                        if(0<=dayofweek<=3):
                            if (hours + sum_hours > HoursLaborableKindOfDay):
                                #print("The sum of unavailable hours at " + str(day_range) + " is not allowed (>8.5h).")
                                raise forms.ValidationError({'hours': ["The sum of unavailable hours at " + str(day_range) + " is not allowed (>"+str(HoursLaborableKindOfDay)+"h).",]})
                        elif(dayofweek==4):
                            if (hours + sum_hours > HoursIntensiveKindOfDay):
                                #print("The sum of unavailable hours at " + str(day_range) + " is not allowed (>7h).")
                                raise forms.ValidationError({'hours': ["The sum of unavailable hours at " + str(day_range) + " is not allowed (>7"+str(HoursIntensiveKindOfDay)+"h).",]})
            elif (type_hours_input=="whole_day"):
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
    #YEAR_CHOICES =  (('All','  All'),(str(currentYear+1),str(currentYear+1)), (str(currentYear),str(currentYear)),(str(currentYear-1),str(currentYear-1)),(str(currentYear-2),str(currentYear-2)))
    #MONTH_CHOICES = (('All','  All'),('1','January'), ('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','Desember'))
    #WEEK_CHOICES = (('All', '  All'),(currentWeek,'Current'))


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
    year_selector = forms.ChoiceField(label='Year',choices=(('All', 'All'),) + YEAR_CHOICES)
    month_selector = forms.ChoiceField(label='Month',choices=(('All', 'All'),) + MONTH_CHOICES)
    week_selector = forms.ChoiceField(label='Week',choices= WEEK_CHOICES)
    

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

    year_selector = forms.ChoiceField(label='Year',choices=YEAR_CHOICES)
    month_selector = forms.ChoiceField(label='Month',choices=MONTH_CHOICES)
    mode_selector = forms.ChoiceField(label='Mode',choices=MODE_CHOICES)
    #change
    location_selector = forms.ChoiceField(label='Location', choices=LOCATION_CHOICES)

    def __init__(self, user, location_choices, *args, **kwargs):
       super(CalendarFilterForm, self).__init__(*args, **kwargs)
       self.fields['location_selector'].choices = location_choices


    def save(self, commit=True):
        #print("> INFO, forms.py: save() method")
        year = self.cleaned_data.get('year_selector', None)
        month = self.cleaned_data.get('month_selector', None)
        mode = self.cleaned_data.get('mode_selector', None)
        location = self.cleaned_data.get('location_selector', None)
        #print("INFO: FORMS.CalendarFilterForm.save "+ location + ", " + mode + ", " + year + ", " + month)
        return(location, mode, year, month)

    def clean_location_selector(self):
        #print ("INFO: FORMS.ListFilterForm.clean, ")
        data = self.cleaned_data.get('location_selector')
        data = self.cleaned_data['location_selector']
        #print("INFO: FORMS.ListFilterForm.clean, " + str(data))
        return data

class CalendarEventFilterForm(forms.Form):

    #location_selector = forms.ChoiceField(label='Location', choices=[(choice.pk, choice) for choice in Location.objects.all().order_by('location')])
    location_selector = forms.ChoiceField(label='Location', choices=LOCATION_CHOICES)
    kindofday_selector = forms.ChoiceField(label='KindOfDay', choices=[(choice.pk, choice) for choice in KindOfDay.objects.all().order_by('kindofday')])

    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    """
    YEAR_CHOICES =  ((str(currentYear+1),str(currentYear+1)), (str(currentYear),str(currentYear)),(str(currentYear-1),str(currentYear-1)),(str(currentYear-2),str(currentYear-2)))
    MONTH_CHOICES = (('All', 'All'), ('1','January'), ('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','Desember'))
    """
    year_selector = forms.ChoiceField(label='Year',choices=YEAR_CHOICES)
    month_selector = forms.ChoiceField(label='Month',choices=MONTH_CHOICES)

    def __init__(self, user, location_choices, kindofday_choices, *args, **kwargs):
       super(CalendarEventFilterForm, self).__init__(*args, **kwargs)
       self.fields['location_selector'].choices = location_choices
       self.fields['kindofday_selector'].choices = kindofday_choices

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
    location_selector = forms.ChoiceField(label='Location', choices=LOCATION_CHOICES)
    hidden_type_date_input = forms.CharField()
    date_selector = forms.DateField(initial=date.today, widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = CalendarEvent
        fields = ('kindofday', 'start_date', 'end_date','comment')

        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, user, location_choices, kindofday_choices, location, *args, **kwargs):
       super(CalendarEventForm, self).__init__(*args, **kwargs)
       self.fields['location_selector'].choices = location_choices
       self.fields['kindofday'].choices = kindofday_choices
       self.fields['start_date'].required = False
       self.fields['end_date'].required = False
       self.fields['date_selector'].required = False

       if (location != ""):
           self.fields['location_selector'].initial = location
       self.user=user
       
       #print ("INFO: FORMS.CalendarEventForm.__init__, event_id=" + str(event_id))

    def save(self, commit=True):
        location = self.cleaned_data.get('location_selector', None)
        if (location != "All"):
            location_id = self.cleaned_data.get('location_selector', None)
            location = Location.objects.get(id=location_id)
          
        kindofday = self.cleaned_data.get('kindofday', None)
        type_date_input = self.cleaned_data.get('hidden_type_date_input')
        if(type_date_input=="single_date"):
            start_date = self.cleaned_data.get('date_selector')
            end_date = start_date
        else:
            start_date = self.cleaned_data.get('start_date', None)
            end_date = self.cleaned_data.get('end_date', None)
        comment = self.cleaned_data.get('comment', None)
        print("INFO: FORMS.CalendarEventForm.save: " + str(location) + ", " + str(kindofday) + ", " + str(start_date) + ", " + str(end_date) + ", " + str(comment) + ", ")
        return (location, kindofday, start_date, end_date, comment)

    def clean_location_selector(self):
        #print ("INFO: FORMS.ListFilterForm.clean, ")
        data = self.cleaned_data.get('location_selector')
        data = self.cleaned_data['location_selector']
        #print("INFO: FORMS.ListFilterForm.clean, " + str(data))
        return data
    def clean_start_date(self):
        #print ("INFO: FORMS.ListFilterForm.clean, ")
        data = self.cleaned_data.get('start_date')
        data = self.cleaned_data['start_date']
        #print("INFO: FORMS.ListFilterForm.clean, " + str(data))
        return data
    def clean_end_date(self):
        #print ("INFO: FORMS.ListFilterForm.clean, ")
        data = self.cleaned_data.get('end_date')
        data = self.cleaned_data['end_date']
        #print("INFO: FORMS.ListFilterForm.clean, " + str(data))
        return data

    def clean(self):
        type_date_input = self.cleaned_data.get('hidden_type_date_input')
        location = self.cleaned_data.get('location_selector')
        #print(location)
        if (location == ""):
            raise forms.ValidationError({'location': ["This field is required.",]})
            print("Invalid Location selection")
        if(type_date_input=="single_date"):
            date = self.cleaned_data.get('date_selector')
            #print(date)
            if (date==None):
                raise forms.ValidationError({'date_selector': ["This field is required.",]})
        else:
            start_date = self.cleaned_data.get('start_date') 
            end_date = self.cleaned_data.get('end_date')
            if (start_date == None):
                raise forms.ValidationError({'start_date': ["This field is required.",]})
            if (end_date == None):
                raise forms.ValidationError({'end_date': ["This field is required.",]})
            if (end_date < start_date):
                raise forms.ValidationError({'start_date': ["Finish date cannot be previous to Start date.",]})

class CalendarEventEditForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ('location', 'kindofday', 'start_date', 'end_date','comment')

        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, user, location_choices, kindofday_choices, *args, **kwargs):
       super(CalendarEventEditForm, self).__init__(*args, **kwargs)
       self.fields['location'].choices = location_choices
       self.user=user
       self.fields['kindofday'].choices = kindofday_choices
       #print ("INFO: FORMS.CalendarEventForm.__init__, event_id=" + str(event_id))

    def clean(self):
        #print("RegisterForm: CLEAN")
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        if(start_date>end_date):
            raise forms.ValidationError({'start_date': ["The Start Date cannot be older than the End Date.",]})
            print("Oops!  That was no valid date.  Try again...")  

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        #fields = ('employee_id', 'phone', 'location')
        fields = ('employee_id', 'phone')
