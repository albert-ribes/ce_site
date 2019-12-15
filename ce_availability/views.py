from django.shortcuts import render

# Create your views here.
from .models import Register, Unavailability, Category, CalendarEvent, KindOfDay, Location, Employee
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django import forms
from .forms import RegisterForm, ListFilterForm, UserForm, EmployeeForm, CalendarFilterForm, CalendarEventForm, CalendarEventEditForm, CalendarEventFilterForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from datetime import datetime, timedelta, date
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from calendar import monthrange, month_name
from operator import itemgetter
from django.template import RequestContext
import logging

log = logging.getLogger(__name__)

def home(request):
    return render(request, 'ce_availability/home.html')
def edit(request):
    return render(request, 'ce_availability/edit.html')

def getUserType(user):
    groups = user.groups.all()
    for group in groups:
        if group.name=='CE':
            user_type='CE'
        if group.name=='SDM':
            user_type='SDM'
        if group.name=='Admin':
            user_type='Admin'
        if group.name=='SUPER':
            user_type='SUPER'
    return user_type

@login_required
def day_info(request, ce, year, month, day):
    employee=User.objects.filter(id=ce).get()
    datetime=date(int(year), int(month), int(day))
    location_id=Employee.objects.filter(user_id=employee.id).values_list('location', flat=True).get()
    #print("INFO: " + str(datetime) + ", location_id:" + str(location_id))
    calendar_events=CalendarEvent.objects.filter(start_date__lte=datetime).filter(end_date__gte=datetime).filter(location=location_id).order_by('start_date')
    #print(calendar_events)
    data={
        'calendar_events': calendar_events,
        'employee': employee,
        'year': year,
        'month': month,
        'day':day,
    }
    return render(request, 'ce_availability/day_info.html', data)

@login_required
def registers_ce_day(request, ce, year, month, day):
    #print("INFO: VIEWS.registers_ce_day: ce=" + ce + ", year=" + year + ", month=" + month + ", day", day)
    queryset = Register.objects.filter(user_id=ce).filter(date__year=year).filter(date__month=month).filter(date__day=day).order_by('-date')
    registers = queryset
    hours=0
    for register in registers:
        hours = hours + register.hours

    user=User.objects.filter(id=ce).get()
    #print("EMPLOYEE" + str(user))
    
    data={
        'registers': registers,
        'hours': hours,
        'year': year,
        'month': month,
        'day':day,
        'employee': user
    }
    return render(request, 'ce_availability/registers_ce_day.html', data)

@login_required
def list_filter(request, ce, unavailability, category, year, month, week):
    user=request.user
    log.info("VIEWS.PY: LIST accessed by " + user.username)
    #print("INFO: VIEWS.list_filter: ce=" + ce + ", unavailability=" + unavailability + ", year=" + year + ", month=" + month) 
    request.session['url'] = "/ce_availability/list/" + str(ce) + "/" + str(unavailability) + "/" + str(category) + "/" + str(year) + "/" + str(month) + "/"  + str(week) 

    #print("INFO: VIEWS.list_filter: user.id=" + str(user.id))
    user_type=getUserType(user)
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    currentWeek = datetime.now().isocalendar()[1]
    firstDayWeek = datetime.now() - timedelta(days=datetime.now().weekday())
    lastDayWeek = firstDayWeek + timedelta(days=6)
    #print("INFO: VIEWS.list_filter: currentYear=" + str(currentYear) + ", currentMonth=" + str(currentMonth))
    #print("INFO: VIEWS.list_filter: currentWeek=" + str(currentWeek) + ", firstDayWeek=" + str(firstDayWeek.day)  + ", lastDayWeek=" + str(lastDayWeek.day))

    if user_type=='CE':
       if (ce!=str(user.id)):
           return HttpResponseRedirect("/ce_availability/list")
       manager_id=user.employee.manager.id
       ce_choices=[(choice.pk, choice.last_name + ", " + choice.first_name) for choice in User.objects.filter(id=ce).order_by('last_name')]
    if user_type=='SDM':
       manager_id=user.id
       ce_choices=[(choice.pk, choice.last_name + ", " + choice.first_name) for choice in User.objects.filter(groups__name='CE').filter(employee__manager=manager_id).order_by('last_name')]
       ce_choices= [('All', 'All')] + ce_choices
    if user_type=='SUPER':
       manager_id=0
       ce_choices=[(choice.pk, choice.last_name + ", " + choice.first_name) for choice in User.objects.filter(groups__name='CE').order_by('last_name')]
       ce_choices= [('All', 'All')] + ce_choices
    """ 
    for choice in ce_choices:
             print(choice)
    """

    # If this is a POST request then process the Form data
    if request.method == "POST":
        # Create a form instance and populate it with data from the request (binding):
        form = ListFilterForm(request.user, ce_choices, request.POST)
         # Check if the form is valid:
        if form.is_valid():
            #print("INFO: VIEWS.list: form.is_valid()")
            # process the data in form
            ce, unavailability, category, year, month, week = form.save(commit=False)
            if(year=='All' or month=='All'):
                week='All'
            if(year!=str(currentYear) or month!=str(currentMonth)):
                week='All'
            request.session['url'] = "/ce_availability/list/" + str(ce) + "/" + str(unavailability) + "/" + str(category) + "/" + str(year) + "/" + str(month + "/" + str(week))
            #print("INFO: VIEWS.list: URL=" + request.session['url'])
            return HttpResponseRedirect("/ce_availability/list/" + str(ce) + "/" + str(unavailability) + "/" + str(category) + "/" + str(year) + "/" + str(month) + "/" +  str(week))
    #If this is a GET (or any other method) create the default form.
    else:
        if(user_type=='SDM'):
            sdm=user.id
        else:
            sdm=user.employee.manager
        if(year=='All'):
            start_year=2000
            end_year=currentYear
        else:
            start_year=year
            end_year=year
        if(month=='All'):
            start_month=1
            end_month=12
        else:
            start_month=month
            end_month=month
            
        #queryset = Register.objects.filter(start_date__year__gte=start_year).filter(start_date__year__lte=end_year).filter(start_date__month__gte=start_month).filter(start_date__month__lte=end_month).order_by('-start_date')
        queryset = Register.objects.order_by('-date')
        if (ce=='All'):
            if (user_type!='SUPER'):
                queryset = queryset.filter(user__employee__manager=manager_id)
        else:
            queryset = queryset.filter(user_id=ce)
        if (unavailability!='All'):
            queryset = queryset.filter(unavailability=unavailability)
            category=Unavailability.objects.filter(id=unavailability).values_list('category_id', flat=True).get()
            #print("INFO: VIEWS.list_filter: category_selector=" + str(category))
        if (category!='All' and unavailability=='All'):
            queryset = queryset.filter(unavailability__category=category)
            #print(queryset)
            category_selector=category
            unavailability='All'
        """
        if (unavailability!='All'):
            queryset = queryset.filter(unavailability=unavailability)
        """

        #print("WEEK=" + week + ": " + str(firstDayWeek.year) + "-" + str(firstDayWeek.month) + "-" + str(firstDayWeek.day)  + ", " + str(lastDayWeek.year) + "-" +str(lastDayWeek.month) + "-" + str(lastDayWeek.day))
        if(week!='All'):
            queryset = queryset.filter(date__range=(firstDayWeek, lastDayWeek))
        
        elif(year!='All' and month!='All'):
            queryset = queryset.filter(date__year=year).filter(date__month=month)
        elif(year!='All' and month=='All'):
            queryset = queryset.filter(date__year=year)
            week='All'
        elif(year=='All' and month!='All'):
            queryset = queryset.filter(date__month=month)
            week='All'
        if(year!=str(currentYear) or month!=str(currentMonth)):
            week='All'
        
        registers = queryset
        hours=0
        for register in registers:
            hours = hours + register.hours
        
        #print("INFO: VIEWS.list_filter: month=" + month)
        initial = {
            'ce_selector': ce,
            'category_selector': category,
            'year_selector': year,
            'month_selector': month,
            'unavailability_selector':unavailability,
            'week_selector':week
        }
        form = ListFilterForm(request.user, ce_choices, initial)
    return render(request, 'ce_availability/list.html', {'registers': registers, 'form': form, 'hours': hours})

@login_required
def about(request):
    return render(request, 'ce_availability/about.html')


@login_required
def calendar_filter(request, location, mode, year, month):
    user=request.user
    log.info("VIEWS.PY: CALENDAR accessed by " + user.username)
    initial = {
        'location_selector': location,
        'mode_selector': mode,
        'year_selector': year,
        'month_selector': month,
    }
    #print(initial)
    
    #print(user.employee.location)

    if (int(month)>12):
        return HttpResponseRedirect("/ce_availability/calendar/")
    hours=0,5
    first_day_of_week, last_day = monthrange(int(year), int(month))
    monthname=month_name[int(month)]
    #print("MONTH=" + month)
    if(month==str(1)):
        prev_url="/ce_availability/calendar/"+location+"/"+mode+"/"+str(int(year)-1)+"/12"
        next_url="/ce_availability/calendar/"+location+"/"+mode+"/"+year+"/"+str(int(month)+1)+"/"
    elif(month==str(12)):
        prev_url="/ce_availability/calendar/"+location+"/"+mode+"/"+year+"/"+str(int(month)-1)+"/"
        next_url="/ce_availability/calendar/"+location+"/"+mode+"/"+str(int(year)+1)+"/1"
    else:
        prev_url="/ce_availability/calendar/"+location+"/"+mode+"/"+year+"/"+str(int(month)-1)+"/"
        next_url="/ce_availability/calendar/"+location+"/"+mode+"/"+year+"/"+str(int(month)+1)+"/"
    #print("URLS: " + prev_url + ", " + next_url)

    """ -------- PROCESSAMENT DADES EMPLOYEE/MONTH/DAY/HOURS -------- 

    day_of_week[day] = "Weekend" | "Intensive" | "WorkingDay" | "Festive"
    dayofweek[day]= 1|2|3...7
    employee_day_kindofday[employee][day] = "Weekend" | "Intensive" | "WorkingDay" | "Festive"
    employee_day_nahours[employee][day] = {hours}
    employee_day_napercent[employee][day] = {percent}
    employee_day_category[employee][day] = {category}
    sum_hours[employee] = hours
    sum_hours_month[employee] = hours
    percentage[employee]= %

    """
    month_range = range(1, last_day + 1)
    day_of_week = {}
    day_week = first_day_of_week
    datetime_first_day_of_week = date(int(year), int(month), 1)
    datetime_last_day_of_week = date(int(year), int(month), int(last_day))
    #print(datetime_first_day_of_week)
    #print(datetime_last_day_of_week)

    #calendar_events=CalendarEvent.objects.filter(start_date__lte=datetime_last_day_of_week).filter(end_date__gte=datetime_first_day_of_week).filter(location=user.employee.location).order_by('start_date')
    #print(calendar_events)

    day_of_the_week = {}
    for day in month_range:
        day_of_the_week[day] = date(int(year), int(month), day).weekday()
        #print(day_of_the_week[day])

    for day in month_range:
        if(5==day_week or day_week==6):
            day_of_week[day]="Weekend"
        elif(day_week==4):
            day_of_week[day]="Intensive"
        else:
            day_of_week[day]="WorkingDay"
        if (day_week==6):
            day_week=0
        else:
            day_week = day_week + 1

    user=request.user
    #print(user.id)
    user_type=getUserType(user)
    #print(user_type)

    if user_type=='CE':
       manager_id=user.employee.manager.id
       employees=User.objects.filter(id=user.id)
       employee_count = 1
       employee_location=Employee.objects.filter(id=user.id).values_list('location', flat=True).get()
       #print("employee_location: " + str(employee_location))

       manager_id=str(user.employee.manager.id)
       location_choices=[(choice.pk, choice.location) for choice in Location.objects.filter(id=user.employee.location.id).order_by('location')]
       #print(location_choices)

    if user_type=='SDM':
       manager_id=user.id
       #ce='All'
       employees = User.objects.filter(groups__name='CE').filter(employee__manager=manager_id).order_by('employee__location','last_name')#.order_by('last_name')
       if (location!="all" and location!="All"):
           employees = employees.filter(employee__location_id=location)
       employee_count=employees.count()
       #print(employee_count)
       location_choices=[(choice.pk, choice.location) for choice in Location.objects.filter(manager_id=manager_id).order_by('location')]
       location_choices= [('All', 'All')] + location_choices

    if user_type=='SUPER':
       #manager_id=user.id
       #ce='All'
       employees = User.objects.filter(groups__name='CE').order_by('employee__location','last_name')#.order_by('last_name')
       if (location!="all" and location!="All"):
           employees = employees.filter(employee__location_id=location)
       employee_count=employees.count()
       #print(employee_count)
       location_choices=[(choice.pk, choice.location) for choice in Location.objects.order_by('location')]
       location_choices= [('All', 'All')] + location_choices

    #print(location_choices)
    employee_day_kindofday={} 
    for employee in employees:
        #print(employee.username + " - " + employee.employee.location.loc_short)
        employee_day_kindofday[employee.username]={}
        #print("-------------------------------------------------")
        #print(">>>" + employee.username + ", ID=" + str(employee.id))
        location_id=Employee.objects.filter(user_id=employee.id).values_list('location', flat=True).get()
        #print(str(datetime_last_day_of_week) + ", " + str(datetime_first_day_of_week) + ", " + str(location_id))
        #calendar_events=CalendarEvent.objects.filter(start_date__lte=datetime_last_day_of_week).filter(end_date__gte=datetime_first_day_of_week).filter(location=location_id).order_by('start_date')
        calendar_events=CalendarEvent.objects.filter(start_date__lte=datetime_first_day_of_week).filter(end_date__gte=datetime_first_day_of_week).filter(location=location_id).order_by('start_date') | CalendarEvent.objects.filter(start_date__gte=datetime_first_day_of_week).filter(end_date__gte=datetime_first_day_of_week).filter(location=location_id).order_by('start_date')
        #print(calendar_events)
        loc=Location.objects.filter(id=location_id).get()
        #print("@" + str(loc))
        day_week=first_day_of_week
        for day in month_range:
            if(5==day_week or day_week==6):
                employee_day_kindofday[employee.username][day]="Weekend"
            elif(day_week==4):
                employee_day_kindofday[employee.username][day]="Intensive"
            else:
                employee_day_kindofday[employee.username][day]="WorkingDay"
            if (day_week==6):
                day_week=0
            else:
                day_week = day_week + 1

        for event in calendar_events:
            delta = event.end_date - event.start_date
            #print(event)
            for i in range(delta.days+1):
                day_event=event.start_date + timedelta(days=i)
                #print("---" + str(day_event))
                #print(str(day.year) + "-"+ str(day.month) + "-" + str(day.day) + ", weekday=" + str(day.weekday()))
                if(str(day_event.month) == month and day_event.weekday()!=6 and day_event.weekday()!=5 and employee_day_kindofday[employee.username][day_event.day]!="Festive"):
                    employee_day_kindofday[employee.username][day_event.day]=event.kindofday.kindofday
                    #print("---" + str(day_event) + " " + employee_day_kindofday[employee.username][day_event.day])

    #print(" ################################################# ")

    #employee_day_hours[employee.username][day]={hours} conté el llistat d'hores NA per empleat al mes
    #employee_day_hours_percent[employee.username][day]={hours} conté el llistat en percentatge d'hores NA per empleat al mes
    employee_day_nahours={}
    employee_day_nahours_percent={}
    employee_day_category={}

    categories = Category.objects.all()
    category_hours={}
    for category in categories:
        #print(category.short_name)
        category_hours[category.short_name]=0
    #print(category_hours)

    for employee in employees:
        employee_day_nahours[employee.username]={}
        employee_day_nahours_percent[employee.username]={}
        employee_day_category[employee.username]={}
        #print("\n>>>>>>>>>>>>>>>>>>>>>>>>>> " +str(employee) + " >>>>>>>>>>>>>>>>>>>>>>>>>>")
        registers=Register.objects.filter(date__year=year).filter(date__month=month).filter(user_id=employee)
        #print(str(registers))
        for day in month_range:
            employee_day_nahours[employee.username][day]={}
            employee_day_nahours_percent[employee.username][day]={}
            employee_day_category[employee.username][day]={}
            hours=0
            registers_day=registers.filter(date__day=day)
            #print("#" +str(day) + ", ") #+ str(registers_day))

            for category in category_hours:
                category_hours[category] = 0

            for r in registers_day:
                #print(r)
                hours = hours + r.hours
                """Category"""
                category = r.unavailability.category
                category_hours[r.unavailability.category.short_name]=category_hours[r.unavailability.category.short_name]+r.hours
                #print(str(category) + ", hours=" + str(r.hours))
            if(registers_day):
                max_category=max(category_hours.items(), key=itemgetter(1))[0]
                employee_day_category[employee.username][day]=max_category
            #print("- Category: " + str(employee_day_category[employee.username][day]))
            #print(max_category)
            if(employee_day_kindofday[employee.username][day]=="WorkingDay"):
                #total_hours=8.5
                total_hours = KindOfDay.objects.filter(kindofday="WorkingDay").values_list('laborablehours', flat=True).get()
            if(employee_day_kindofday[employee.username][day]=="Intensive"):
                #total_hours=7
                total_hours = KindOfDay.objects.filter(kindofday="Intensive").values_list('laborablehours', flat=True).get()
            if(employee_day_kindofday[employee.username][day]=="Festive"):
                total_hours=0.1
            if(employee_day_kindofday[employee.username][day]=="Weekend"):
                total_hours=0.1
            #print(total_hours)
            hours_percent=1-hours/total_hours
            hours_percent=format(hours_percent, '.2f')
            #print(employee.username + ", " + str(day) + ", " + str(hours))
            employee_day_nahours[employee.username][day]={hours}
            employee_day_nahours_percent[employee.username][day]={hours_percent}
            #print(employee.username + ", " + str(day) + ", " + str(employee_day_hours[employee.username][day]))
            #print(employee.username + ", " + str(day) + ", " + str(employee_day_hours_percent[employee.username][day]))

    #sum_hours: suma d'hores NA per Employee al mes
    employee_nahours_month={}
    sum_hours = {}
    for employee, value in employee_day_nahours.items():
        sum_hours[employee]=0
        employee_nahours_month[employee]=0
        for day, hours in value.items():
            for h in hours:
                #print(str(usr) + ", " +str(day)+", " + str(h))
                sum_hours[employee]+=h
                employee_nahours_month[employee]+=h 
    #print(sum_hours)

    #hours_month: suma d'hores laborables del mes
    employee_total_hours_month={}
    percentage = {}
    for employee in employees:
        employee_total_hours_month[employee.username]=0
        #print("<<<<" + employee.username)
        for day, kind_day in employee_day_kindofday[employee.username].items():
            #print(str(day) + ", " + kind_day)
            if (kind_day=="WorkingDay"):
                employee_total_hours_month[employee.username]=employee_total_hours_month[employee.username] + KindOfDay.objects.filter(kindofday="WorkingDay").values_list('laborablehours', flat=True).get()
            elif (kind_day=="Intensive"):
                employee_total_hours_month[employee.username]=employee_total_hours_month[employee.username] + KindOfDay.objects.filter(kindofday="Intensive").values_list('laborablehours', flat=True).get()
            else:
                employee_total_hours_month[employee.username]=employee_total_hours_month[employee.username] + 0


        percentage[employee.username]=100*employee_nahours_month[employee.username]/employee_total_hours_month[employee.username]
        percentage[employee.username]=format(percentage[employee.username], '.2f')

        #print(employee_nahours_month[employee.username])
        #print(employee_total_hours_month[employee.username])
        #print(percentage[employee.username])
    #print(" ################################################# ")

    hours_month = 0
    sum_hours_month = {}
    for day, kind_day in day_of_week.items():
       #print(str(day) + ", " + kind_day)
       if(kind_day=="WorkingDay"):
           hours_month+=8.5
       if(kind_day=="Intensive"):
           hours_month+=7
    #print(hours_month)

    #print(percentage)

    if request.method == "POST":
        # Create a form instance and populate it with data from the request (binding):
        form = CalendarFilterForm(request.user, location_choices, request.POST)
         # Check if the form is valid:
        if form.is_valid():
            #print("INFO: VIEWS.list: form.is_valid()")
            # process the data in form
            location, mode, year, month = form.save(commit=False)
            form_url="/ce_availability/calendar/"+location+"/"+mode+"/"+year+"/"+month+"/"
            #return render(request, 'ce_availability/calendar.html', {'registers': registers, 'form': form, 'hours': hours})
            return HttpResponseRedirect(form_url)
    #If this is a GET (or any other method) create the default form.
    else:

        #print("initial-------------" + str(initial))
        form = CalendarFilterForm(request.user, location_choices, initial)

    #print(employee_day_category)
    #print(request.user)
    data = {
        'employee_day_nahours': employee_day_nahours,
        'employee_day_nahours_percent': employee_day_nahours_percent,
        'employee_day_kindofday': employee_day_kindofday,
        'employee_nahours_month': employee_nahours_month,
        'employee_total_hours_month': employee_total_hours_month,
        'employee_day_category': employee_day_category,
        'day_of_week': day_of_week,
        'day_of_the_week': day_of_the_week,
        'employees': employees, 
        'year':year,'month': month, 'monthname':monthname,
        'first_day_of_week': first_day_of_week,
        'month_range':month_range ,
        'hours':hours,
        'next_url':next_url,
        'prev_url': prev_url,
        'sum_hours': sum_hours,
        'hours_month': hours_month,
        'percentage':percentage,
        'form': form,
        'mode': mode,
        'user_type': user_type,
        'employee_count': employee_count
    }
    #print(data)
    #print(employee_total_hours_month)
    #print(percentage)
    return render(request, 'ce_availability/calendar.html', data)

@login_required
def calendar(request):
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    user=request.user
    user_type=getUserType(user)
    #print("####: " + str(user_type))
    if user_type=='CE':
       mode="hours"
       location=user.employee.location
    if user_type=='SDM':
       mode="percentage"
       location="all"
    if user_type=='SUPER':
       mode="percentage"
       location="all"    
    #print("####: " + str(location))
    return HttpResponseRedirect("/ce_availability/calendar/" + str(location) + "/" + mode + "/" + str(currentYear) + "/" + str(currentMonth))


@login_required
def calendar_edit(request):
    user=request.user
    user_type=getUserType(user)
    if user_type!='SDM' and user_type!='SUPER':
       return HttpResponseRedirect("/ce_availability/calendar/")
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    currentWeek = datetime.now().isocalendar()[1]

    #print("INFO: VIEWS.list: usertype=" + user_type)

    if user_type=='CE':
       manager_id=user.employee.manager.id
       ce=user.id
    if user_type=='SDM':
       manager_id=user.id
       ce='All'
    if user_type=='SUPER':
       #manager_id=user.id
       ce='All'
    location='All'
    kindofday='All'
    return HttpResponseRedirect("/ce_availability/calendar_edit/" + str(location) + "/" + str(kindofday) + "/" + str(currentYear) + "/" + str(currentMonth))

@login_required
def calendar_edit_filter(request, location, kindofday, year, month):
    request.session['url'] = "/ce_availability/calendar_edit/" + str(location) + "/" + str(kindofday) + "/" + str(year) + "/" + str(month)
    #print (request.session['url'])
    initial = {
        'location_selector': location,
        'kindofday_selector': kindofday,
        'year_selector': year,
        'month_selector': month,
    }

    #print(initial)

    queryset = CalendarEvent.objects.filter(start_date__year=year).order_by('-start_date')
    if (month !="All"):
        queryset = queryset.filter(start_date__month=month)
    if (location !="All"):
        queryset = queryset.filter(location=location)
    if (kindofday != "All"):
        queryset = queryset.filter(kindofday=kindofday)
    calendar_events = queryset

    user = request.user
    manager_id=user.id
    location_choices=[(choice.pk, choice.location) for choice in Location.objects.filter(manager_id=manager_id).order_by('location')]
    location_choices= [('All', 'All')] + location_choices
    kindofday_choices=[(choice.pk, choice.kindofday) for choice in KindOfDay.objects.filter(kindofday="Intensive").order_by('kindofday')]
    kindofday_choices = [(choice.pk, choice.kindofday) for choice in KindOfDay.objects.filter(kindofday="Festive").order_by('kindofday')] + kindofday_choices
    kindofday_choices = [('All', 'All')] + kindofday_choices

    if request.method == "POST":
        #print("request.method == POST")
        form = CalendarEventFilterForm(request.user, location_choices, kindofday_choices, request.POST)
        if form.is_valid():
            # print("INFO: VIEWS.list: calendar_edit_filter.is_valid()")
            # process the data in form
            location, kindofday, year, month = form.save(commit=False)
            return HttpResponseRedirect("/ce_availability/calendar_edit/" + str(location) + "/" + str(kindofday) + "/" + str(year) + "/" + str(month))
    else:
        form = CalendarEventFilterForm(request.user, location_choices, kindofday_choices, initial)

    #print(employee_day_category)
    data = {
        'calendar_events':calendar_events,
        'form': form,
    }

    return render(request, 'ce_availability/calendar_edit.html', data)


@login_required
def list(request):
    user=request.user
    user_type=getUserType(user)
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    currentWeek = datetime.now().isocalendar()[1]

    #print("INFO: VIEWS.list: usertype=" + user_type)

    if user_type=='CE':
       manager_id=user.employee.manager.id
       ce=user.id
    if user_type=='SDM':
       manager_id=user.id
       ce='All'
    if user_type=='SUPER':
       manager_id=user.id
       ce='All'
    unavailability='All'
    category='All'
    return HttpResponseRedirect("/ce_availability/list/" + str(ce) + "/" + str(unavailability) + "/" + str(category) + "/" + str(currentYear) + "/" + str(currentMonth) + "/" + str(currentWeek))

@login_required
def insert_event(request):

    user = request.user
    manager_id=user.id

    #print ("INFO: VIEWS.event_details: event_id=" + str(pk) + ", event details: " + str(event))     
    user = request.user
    manager_id=user.id
    location_choices=[(choice.pk, choice.location) for choice in Location.objects.filter(manager_id=manager_id).order_by('location')]
    location_choices = [('All', 'All')] + location_choices
    location_choices = [('', '------')] + location_choices

    #for location in location_choices:
        #print(location)

    kindofday_choices=[(choice.pk, choice.kindofday) for choice in KindOfDay.objects.filter(kindofday="Intensive").order_by('kindofday')]
    kindofday_choices = [(choice.pk, choice.kindofday) for choice in KindOfDay.objects.filter(kindofday="Festive").order_by('kindofday')] + kindofday_choices
    kindofday_choices = [('', '------')] + kindofday_choices
    location = ""
    #print(location_choices)
    if request.method == "POST":
        locations=Location.objects.filter(manager_id=manager_id).order_by('location')
        #print("INFO: VIEWS.register_details: POST")
        form = CalendarEventForm(user, location_choices, kindofday_choices, location, request.POST)
        #print("INFO: VIEWS.register_details: form=" +str(form))
        if form.is_valid():
            #print("INFO: VIEWS.register_details: FORM_IS_VALID")
            location, kindofday, start_date, end_date, comment = form.save(commit=False)
            print("location=" + str(location) + ", kindofday=" + str(kindofday) + ", start_date=" + str(start_date) + ", end_date=" + str(end_date) + ", comment=" + str(comment))
            if (location == 'All'):
                id=""
                for loc in locations:
                    event = CalendarEvent.objects.create(location=loc,
                                   kindofday=kindofday,
                                   start_date=start_date,
                                   end_date=end_date,
                                   comment=comment
                                   )
                    event.save()
                    log.info("VIEWS.PY: new EVENT inserted by " + user.username)
                    id = id + ", " + str(event.id)
                    #print(">New insert: ID=" + str(register.id) +",Unavailability="+ str(register.unavailability_id) +",hours="+ str(register.hours) +",comments"+ str(register.comments) +",date="+ str(register.date) +",created_date="+ str(register.created_date) +",user_id="+ str(register.user_id))
                result=True
                id=id[2:]
                data = {
                    'result':result,
                    'id': id
                }
                result=True
            else:
                event = CalendarEvent.objects.create(location=location,
                               kindofday=kindofday,
                               start_date=start_date,
                               end_date=end_date,
                               comment=comment
                               )
                event.save()
                log.info("VIEWS.PY: new EVENT inserted by " + user.username)
                result=True
                data = {
                    'result':result,
                    'id': event.id
                }
            return render(request, 'ce_availability/insert_event_post.html', data)
        """
        else:
            print("INFO: VIEWS.register_details: FORM_IS_NOT_VALID")
        """
    else:
        form = CalendarEventForm(user, location_choices, kindofday_choices, location)
    return render(request, 'ce_availability/insert_event.html', {'form': form})


@login_required
def insert_register(request):

    user=request.user
    user_type=getUserType(user)
    #print("INFO: VIEWS.list_filter: user.id=" + str(user.id) +", user_type=" + user_type)

    if user_type=='CE':
       ce_choices=[(choice.pk, choice.last_name  + ", " + choice.first_name) for choice in User.objects.filter(id=user.id)]
    if user_type=='SDM':
       manager_id=user.id
       ce_choices=[(choice.pk, choice.last_name + ", " + choice.first_name) for choice in User.objects.filter(groups__name='CE').filter(employee__manager=manager_id).order_by('last_name')]
    if user_type=='SUPER':
       manager_id=user.id
       ce_choices=[(choice.pk, choice.last_name + ", " + choice.first_name) for choice in User.objects.filter(groups__name='CE').order_by('last_name')]

    """
    for choice in ce_choices:
       print(choice)
    """
    register_id=0
    if request.method == "POST":
        form = RegisterForm(user, register_id, ce_choices, request.POST)
        ce = form['user'].value()
        #print("INFO: VIEWS.list_filter: ce=" + str(ce))
        if form.is_valid():
            #print("VIEWS: insert, form_is_valid, type_date_input: " + str(form.cleaned_data.get('hidden_type_date_input', None)))
            if (str(form.cleaned_data.get('hidden_type_date_input', None))=="single_date"):
                register = form.save(commit=False)
                register.createdby_id = user.id
                register.user_id = int(ce)
                if (form.cleaned_data.get('hidden_type_hours_input', None)=="whole_day"):
                    hours = 6
                    register.hours = hours
                    dayofweek=register.date.weekday()
                    #print("dayofweek:" + str(dayofweek))
                    #print(register.date)
                    calendar_events = CalendarEvent.objects.filter(start_date__lte=register.date).filter(end_date__gte=register.date).filter(location=user.employee.location)
                    #print(calendar_events)
                    """
                    for event in calendar_events:
                        print(event)
                    """
                    day_with_event = "None"
                    if calendar_events:
                        for event in calendar_events:
                            delta_events = event.end_date - event.start_date
                            for j in range(delta_events.days + 1):
                                day_event = event.start_date + timedelta(days=j)
                                if (register.date==day_event):
                                    #print("-kindofday=" + str(event.kindofday))
                                    if(str(event.kindofday)=="Intensive"):
                                        day_with_event = "Intensive"
                                        #print("Intensive")
                                    elif(str(event.kindofday)=="Festive"):
                                        #print("Festive")
                                        day_with_event = "Festive"
                    if(day_with_event == "Intensive" and 0<=dayofweek<=3):
                        #register = Register()
                        #register.unavailability_id = form.cleaned_data.get('unavailability', None).id
                        register.hours = KindOfDay.objects.filter(kindofday="Intensive").values_list('laborablehours', flat=True).get()
                        #register.comments = form.cleaned_data.get('comments', None)
                        #register.date = day_range
                        #register.created_date = timezone.now()#datetime.now()
                        #register.createdby_id = user.id
                        #register.user_id = int(ce)
                        #register.save()
                        #log.info("VIEWS.PY: new REGISTER inserted by " + user.username)
                        result=True
                        id = str(register.id)
                        register.save()
                        log.info("VIEWS.PY: new REGISTER inserted by " + user.username)
                        result=True
                        data = {
                            'result':result,
                            'id': register.id
                        }
                        #print(">New insert: ID=" + str(register.id) +",Unavailability="+ str(register.unavailability_id) +",hours="+ str(register.hours) +",comments"+ str(register.comments) +",date="+ str(register.date) +",created_date="+ str(register.created_date) +",user_id="+ str(register.user_id))
                    elif(day_with_event!="Festive"):
                        if(0<=dayofweek<=3):
                            #register = Register()
                            #register.unavailability_id = form.cleaned_data.get('unavailability', None).id
                            register.hours = KindOfDay.objects.filter(kindofday="WorkingDay").values_list('laborablehours', flat=True).get()
                            #register.comments = form.cleaned_data.get('comments', None)
                            #register.date = day_range
                            #register.created_date = timezone.now()#datetime.now()
                            #register.createdby_id = user.id
                            #register.user_id = int(ce)
                            #register.save()
                            #log.info("VIEWS.PY: new REGISTER inserted by " + user.username)
                            result=True
                            id = str(register.id)
                            #print(">New insert: ID=" + str(register.id) +",Unavailability="+ str(register.unavailability_id) +",hours="+ str(register.hours) +",comments"+ str(register.comments) +",date="+ str(register.date) +",created_date="+ str(register.created_date) +",user_id="+ str(register.user_id))
                        elif(dayofweek==4):
                            #register = Register()
                            #register.unavailability_id = form.cleaned_data.get('unavailability', None).id
                            register.hours = KindOfDay.objects.filter(kindofday="Intensive").values_list('laborablehours', flat=True).get()
                            #register.comments = form.cleaned_data.get('comments', None)
                            #register.date = day_range
                            #register.created_date = timezone.now()#datetime.now()
                            #register.createdby_id = user.id
                            #register.user_id = int(ce)
                            #register.save()
                            #log.info("VIEWS.PY: new REGISTER inserted by " + user.username)
                            result=True
                            id = str(register.id)
                            #print(">New insert: ID=" + str(register.id) +",Unavailability="+ str(register.unavailability_id) +",hours="+ str(register.hours) +",comments"+ str(register.comments) +",date="+ str(register.date) +",created_date="+ str(register.created_date) +",user_id="+ str(register.user_id))
                        register.save()
                        log.info("VIEWS.PY: new REGISTER inserted by " + user.username)
                        result=True
                        data = {
                            'result':result,
                            'id': register.id
                        }
                else:
                    register.save()
                    log.info("VIEWS.PY: new REGISTER inserted by " + user.username)
                    result=True
                    data = {
                        'result':result,
                        'id': register.id
                    }
                return render(request, 'ce_availability/insert_post.html', data)
            elif (str(form.cleaned_data.get('hidden_type_date_input', None))=="range_date"):
                if (form.cleaned_data.get('hidden_type_hours_input', None)=="whole_day"):
                    id=""
                    result=False
                    start_date = form.cleaned_data.get('start_date')
                    end_date = form.cleaned_data.get('end_date')
                    delta_range = end_date - start_date
                    calendar_events = CalendarEvent.objects.filter(start_date__lte=end_date).filter(end_date__gte=start_date).filter(location=user.employee.location).order_by('start_date')
                    for i in range(delta_range.days + 1):
                        day_range = start_date + timedelta(days=i)
                        dayofweek=day_range.weekday()
                        #print("############ DAY=" + str(day_range) + ", dayofweek: " + str(dayofweek))
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
                            register = Register()
                            register.unavailability_id = form.cleaned_data.get('unavailability', None).id
                            register.hours = KindOfDay.objects.filter(kindofday="Intensive").values_list('laborablehours', flat=True).get()
                            register.comments = form.cleaned_data.get('comments', None)
                            register.date = day_range
                            register.created_date = timezone.now()#datetime.now()
                            register.createdby_id = user.id
                            register.user_id = int(ce)
                            register.save()
                            log.info("VIEWS.PY: new REGISTER inserted by " + user.username)
                            result=True
                            id = id + ", " + str(register.id)
                            #print(">New insert: ID=" + str(register.id) +",Unavailability="+ str(register.unavailability_id) +",hours="+ str(register.hours) +",comments"+ str(register.comments) +",date="+ str(register.date) +",created_date="+ str(register.created_date) +",user_id="+ str(register.user_id))
                        elif(day_with_event!="Festive"):
                            if(0<=dayofweek<=3):
                                register = Register()
                                register.unavailability_id = form.cleaned_data.get('unavailability', None).id
                                register.hours = KindOfDay.objects.filter(kindofday="WorkingDay").values_list('laborablehours', flat=True).get()
                                register.comments = form.cleaned_data.get('comments', None)
                                register.date = day_range
                                register.created_date = timezone.now()#datetime.now()
                                register.createdby_id = user.id
                                register.user_id = int(ce)
                                register.save()
                                log.info("VIEWS.PY: new REGISTER inserted by " + user.username)
                                result=True
                                id = id + ", " + str(register.id)
                                #print(">New insert: ID=" + str(register.id) +",Unavailability="+ str(register.unavailability_id) +",hours="+ str(register.hours) +",comments"+ str(register.comments) +",date="+ str(register.date) +",created_date="+ str(register.created_date) +",user_id="+ str(register.user_id))
                            elif(dayofweek==4):
                                register = Register()
                                register.unavailability_id = form.cleaned_data.get('unavailability', None).id
                                register.hours = KindOfDay.objects.filter(kindofday="Intensive").values_list('laborablehours', flat=True).get()
                                register.comments = form.cleaned_data.get('comments', None)
                                register.date = day_range
                                register.created_date = timezone.now()#datetime.now()
                                register.createdby_id = user.id
                                register.user_id = int(ce)
                                register.save()
                                log.info("VIEWS.PY: new REGISTER inserted by " + user.username)
                                result=True
                                id = id + ", " + str(register.id)
                                #print(">New insert: ID=" + str(register.id) +",Unavailability="+ str(register.unavailability_id) +",hours="+ str(register.hours) +",comments"+ str(register.comments) +",date="+ str(register.date) +",created_date="+ str(register.created_date) +",user_id="+ str(register.user_id))
                elif (form.cleaned_data.get('hidden_type_hours_input', None)=="insert"):
                    #print("insert")
                    id=""
                    result=False
                    start_date = form.cleaned_data.get('start_date')
                    end_date = form.cleaned_data.get('end_date')
                    delta_range = end_date - start_date
                    calendar_events = CalendarEvent.objects.filter(start_date__lte=end_date).filter(end_date__gte=start_date).filter(location=user.employee.location).order_by('start_date')
                    for i in range(delta_range.days + 1):
                        day_range = start_date + timedelta(days=i)
                        dayofweek=day_range.weekday()
                        #print("############ DAY=" + str(day_range) + ", dayofweek: " + str(dayofweek))
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
                    for i in range(delta_range.days + 1):
                        day_range = start_date + timedelta(days=i)
                        dayofweek=day_range.weekday()
                        #print("############ DAY=" + str(day_range) + ", dayofweek: " + str(dayofweek))
                        day_with_event = "None"
                        if((day_with_event!="Festive" or day_with_event=="") & 0<=dayofweek<=4):
                            register = Register()
                            register.unavailability_id = form.cleaned_data.get('unavailability', None).id
                            register.hours = form.cleaned_data.get('hours', None)
                            register.comments = form.cleaned_data.get('comments', None)
                            register.date = day_range
                            register.created_date = timezone.now()#datetime.now()
                            register.createdby_id = user.id
                            register.user_id = int(ce)
                            register.save()
                            log.info("VIEWS.PY: new REGISTER inserted by " + user.username)
                            result=True
                            id = id + ", " + str(register.id)
                            #print(">New insert: ID=" + str(register.id) +",Unavailability="+ str(register.unavailability_id) +",hours="+ str(register.hours) +",comments"+ str(register.comments) +",date="+ str(register.date) +",created_date="+ str(register.created_date) +",user_id="+ str(register.user_id))
                id=id[2:]
                data = {
                    'result':result,
                    'id': id
                }
                return render(request, 'ce_availability/insert_post.html', data)

    else:
        #form = RegisterForm(ce_choices, request.POST)
        form = RegisterForm(user, register_id, ce_choices)
    return render(request, 'ce_availability/insert_register.html', {'form': form})

@login_required
def user_details(request):
    user_type=getUserType(request.user)
    return render(request, 'ce_availability/user_details.html', {'user_type':user_type})

@login_required
def user_settings(request):
    user_type=getUserType(request.user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        employee_form = EmployeeForm(request.POST, instance=request.user.employee)
        if user_form.is_valid() and employee_form.is_valid():
            user_form.save()
            employee_form.save()
            log.info("VIEWS.PY: new USER SETTING modified by " + user.username)
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('/ce_availability')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        employee_form = EmployeeForm(instance=request.user.employee)
    return render(request, 'ce_availability/user_settings.html', {
        'user_form': user_form,
        'employee_form': employee_form,
        'user_type':user_type
    })

@login_required
def settings(request):
    return render(request, 'ce_availability/settings.html')


@login_required
def event_details(request, pk):

    user = request.user
    manager_id=user.id
    event = get_object_or_404(CalendarEvent, pk=pk)
    #print ("INFO: VIEWS.event_details: event_id=" + str(pk) + ", event details: " + str(event))     
    user = request.user
    manager_id=user.id

    location_choices=[(choice.pk, choice.location) for choice in Location.objects.filter(manager_id=manager_id).order_by('location')]
    
    kindofday_choices=[(choice.pk, choice.kindofday) for choice in KindOfDay.objects.filter(kindofday="Intensive").order_by('kindofday')]
    kindofday_choices = [(choice.pk, choice.kindofday) for choice in KindOfDay.objects.filter(kindofday="Festive").order_by('kindofday')] + kindofday_choices

    location = ""
    #print(location_choices)

    if request.method == "POST":
        #print("INFO: VIEWS.register_details: POST")
        form = CalendarEventEditForm(user, location_choices, kindofday_choices, request.POST, instance=event)
        #print("INFO: VIEWS.register_details: form=" +str(form))
        if form.is_valid():
            #print("INFO: VIEWS.register_details: FORM_IS_VALID")
            event = form.save(commit=False)
            event.save()
            result=True
            return render(request, 'ce_availability/update_event_post.html', {'result':result, 'id': event.id})
        """
        else:
            print("INFO: VIEWS.register_details: FORM_IS_NOT_VALID")
        """
    else:
        initial = {
            'kindofday': event.kindofday
        }
        form = CalendarEventEditForm(user, location_choices, kindofday_choices, instance=event)
    return render(request, 'ce_availability/event_details.html', {'form': form, 'event': event})


@login_required
def register_details(request, pk):
    user=request.user
    user_type=getUserType(user)
    #print("INFO: VIEWS.register_details: user.id=" + str(user.id) +", user_type=" + user_type)

    if user_type=='CE':
       ce_choices=[(choice.pk, choice.last_name  + ", " + choice.first_name) for choice in User.objects.filter(id=user.id)]
    if user_type=='SDM':
       manager_id=user.id
       ce_choices=[(choice.pk, choice.last_name  + ", " + choice.first_name) for choice in User.objects.filter(groups__name='CE').filter(employee__manager=manager_id).order_by('last_name')]
    if user_type=='SUPER':
       #manager_id=user.id
       ce_choices=[(choice.pk, choice.last_name  + ", " + choice.first_name) for choice in User.objects.filter(groups__name='CE').order_by('last_name')]

    """
    for choice in ce_choices:
       print(choice)
    """
    register = get_object_or_404(Register, pk=pk)
    register_id=register.id
    if request.method == "POST":
        #print("INFO: VIEWS.register_details: POST")
        form = RegisterForm(user, register_id, ce_choices, request.POST, instance=register)
        #print("INFO: VIEWS.register_details: form=" +str(form))
        if form.is_valid():
            #print("INFO: VIEWS.register_details: FORM_IS_VALID")
            register = form.save(commit=False)
            register.save()
            result=True
            return render(request, 'ce_availability/update_register_post.html', {'result':result, 'id': register.id})
        """
        else:
            print("INFO: VIEWS.register_details: FORM_IS_NOT_VALID")
        """
    else:
        form = RegisterForm(user, register_id, ce_choices, instance=register)
        data = {
            'form':form,
            'register': register,
            'user_type':user_type
        }
    return render(request, 'ce_availability/register_details.html', data)

@login_required
def register_details_popup(request, pk):
    user=request.user
    user_type=getUserType(user)
    #print("INFO: VIEWS.register_details: user.id=" + str(user.id) +", user_type=" + user_type)

    if user_type=='CE':
       ce_choices=[(choice.pk, choice.last_name  + ", " + choice.first_name) for choice in User.objects.filter(id=user.id)]
    if user_type=='SDM':
       manager_id=user.id
       ce_choices=[(choice.pk, choice.last_name  + ", " + choice.first_name) for choice in User.objects.filter(groups__name='CE').filter(employee__manager=manager_id).order_by('last_name')]
    if user_type=='SUPER':
       #manager_id=user.id
       ce_choices=[(choice.pk, choice.last_name  + ", " + choice.first_name) for choice in User.objects.filter(groups__name='CE').order_by('last_name')]

    """
    for choice in ce_choices:
       print(choice)
    """

    register = get_object_or_404(Register, pk=pk)
    #print(register)
    register_id=register.id
    if request.method == "POST":
        print("INFO: VIEWS.register_details: POST")
        form = RegisterForm(user, register_id, ce_choices, request.POST, instance=register)
        #print("INFO: VIEWS.register_details: form=" +str(form))
        if form.is_valid():
            #print("INFO: VIEWS.register_details: FORM_IS_VALID")

            register = form.save(commit=False)
            #register.createdby_id = user.id
            #register.user_id = int(ce)
            register.save()
            result=True
            data = {
                'result':result,
                'id': register.id
            }
            #print(data)
            return render(request, 'ce_availability/update_register_post_popup.html', data)
            """
            register = form.save(commit=False)
            register.save()
            result=True
            return render(request, 'ce_availability/update_register_post_popup.html', {'result':result, 'id': register.id})"""
        """
        else:
             print("INFO: VIEWS.register_details: FORM_IS_NOT_VALID")
        """
    else:
        form = RegisterForm(user, register_id, ce_choices, instance=register)
        data = {
            'form':form,
            'register': register,
            'user_type':user_type
        }
    return render(request, 'ce_availability/register_details_popup.html', data)

@login_required
def register_delete(request, pk):
    register = get_object_or_404(Register, pk=pk)
    id = register.id
    register.delete()
    result=True
    data = {
        'result':result,
        'id': id
    }
    return render(request, 'ce_availability/delete_register_post.html', data)

@login_required
def event_delete(request, pk):
    event = get_object_or_404(CalendarEvent, pk=pk)
    id = event.id
    event.delete()
    result=True
    data = {
        'result':result,
        'id': id
    }
    return render(request, 'ce_availability/delete_event_post.html', data)


@login_required
def register_delete_popup(request, pk):
    register = get_object_or_404(Register, pk=pk)
    id = register.id
    register.delete()
    result=True
    data = {
        'result':result,
        'id': id
    }
    return render(request, 'ce_availability/delete_post_popup.html', data)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            log.info("VIEWS.PY: PASSWORD reseted by " + user.username)
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            #return redirect('home')
            return render(request, 'ce_availability/change_password_post.html')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'ce_availability/change_password.html', {
        'form': form
    })

def handler404(request):
    response = render_to_response('404.html', {},
                              context_instance=RequestContext(request))
    response.status_code = 404
    return response
