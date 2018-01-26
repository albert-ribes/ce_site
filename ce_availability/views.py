from django.shortcuts import render

# Create your views here.
from .models import Register, Unavailability, Category
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django import forms
from .forms import RegisterForm, ListFilterForm, UserForm, EmployeeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from datetime import datetime, timedelta
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from calendar import monthrange, month_name

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
    return user_type

@login_required
def list_filter(request, ce, unavailability, category, year, month, week):

    print("INFO: VIEWS.list_filter: ce=" + ce + ", unavailability=" + unavailability + ", year=" + year + ", month=" + month) 
    request.session['url'] = "/ce_availability/list/filter/" + str(ce) + "/" + str(unavailability) + "/" + str(category) + "/" + str(year) + "/" + str(month) + "/"  + str(week) 
    user=request.user
    print("INFO: VIEWS.list_filter: user.id=" + str(user.id))
    user_type=getUserType(user)
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    currentWeek = datetime.now().isocalendar()[1]
    firstDayWeek = datetime.now() - timedelta(days=datetime.now().weekday())
    lastDayWeek = firstDayWeek + timedelta(days=6)
    print("INFO: VIEWS.list_filter: currentYear=" + str(currentYear) + ", currentMonth=" + str(currentMonth))
    print("INFO: VIEWS.list_filter: currentWeek=" + str(currentWeek) + ", firstDayWeek=" + str(firstDayWeek.day)  + ", lastDayWeek=" + str(lastDayWeek.day))

    if user_type=='CE':
       if (ce!=str(user.id)):
           return HttpResponseRedirect("/ce_availability/list")
       manager_id=user.employee.manager.id
       ce_choices=[(choice.pk, choice.last_name + ", " + choice.first_name) for choice in User.objects.filter(id=ce).order_by('last_name')]
    if user_type=='SDM':
       manager_id=user.id
       ce_choices=[(choice.pk, choice.last_name + ", " + choice.first_name) for choice in User.objects.filter(groups__name='CE').filter(employee__manager=manager_id).order_by('last_name')]
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
            print("INFO: VIEWS.list: form.is_valid()")
            # process the data in form
            ce, unavailability, category, year, month, week = form.save(commit=False)
            if(year=='All' or month=='All'):
                week='All'
            if(year!=str(currentYear) or month!=str(currentMonth)):
                week='All'
            request.session['url'] = "/ce_availability/list/filter/" + str(ce) + "/" + str(unavailability) + "/" + str(category) + "/" + str(year) + "/" + str(month + "/" + str(week))
            print("INFO: VIEWS.list: URL=" + request.session['url'])
            return HttpResponseRedirect("/ce_availability/list/filter/" + str(ce) + "/" + str(unavailability) + "/" + str(category) + "/" + str(year) + "/" + str(month) + "/" +  str(week))
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
            
        queryset = Register.objects.filter(start_date__year__gte=start_year).filter(start_date__year__lte=end_year).filter(start_date__month__gte=start_month).filter(start_date__month__lte=end_month).order_by('-start_date')
        #queryset = Register.objects.filter(start_date__lte=timezone.now()).filter(start_date__year__gte=start_year).filter(start_date__year__lte=end_year).filter(start_date__month__gte=start_month).filter(start_date__month__lte=end_month).order_by('-start_date')
        if (ce=='All'):
            queryset = queryset.filter(user__employee__manager=manager_id)
        else:
            queryset = queryset.filter(user_id=ce)
        if (unavailability!='All'):
            queryset = queryset.filter(unavailability=unavailability)
            #category_selector=getattr(Unavailability.objects.filter(unavailability_id=unavailability), 'category_id')
            category=Unavailability.objects.filter(id=unavailability).values_list('category_id', flat=True).get()
            print("INFO: VIEWS.list_filter: category_selector=" + str(category))
        if (category!='All' and unavailability=='All'):
            queryset = queryset.filter(unavailability__category=category)
            category_selector=category
            unavailability='All'
        if (unavailability!='All'):
            queryset = queryset.filter(unavailability=unavailability)
        if(week!='All' and year!='All' and month!='All'):
            firstDayWeek = datetime.now() - timedelta(days=datetime.now().weekday())
            lastDayWeek = firstDayWeek + timedelta(days=6)
            queryset = queryset.filter(start_date__day__gte=firstDayWeek.day).filter(start_date__day__lte=lastDayWeek.day)
        if(year=='All' or month=='All'):
            week='All'
        if(year!=str(currentYear) or month!=str(currentMonth)):
            week='All'
        registers = queryset
        hours=0
        for register in registers:
            hours = hours + register.hours
        
        print("INFO: VIEWS.list_filter: month=" + month)
        """
        if(user_type=='CE'):
            form = ListFilterForm(request.user, ce_choices, initial={'ce_selector': ce, 'year_selector': year, 'month_selector': month, 'unavailability_selector':unavailability, 'week_selector':week})
        
        else:
            form = ListFilterForm(request.user, ce_choices, initial={'ce_selector': ce, 'year_selector': year, 'month_selector': month, 'unavailability_selector':unavailability, 'week_selector':week})
        """
        form = ListFilterForm(request.user, ce_choices, initial={'ce_selector': ce, 'category_selector': category, 'year_selector': year, 'month_selector': month, 'unavailability_selector':unavailability, 'week_selector':week})
    return render(request, 'ce_availability/list.html', {'registers': registers, 'form': form, 'hours': hours})

@login_required
def about(request):
    return render(request, 'ce_availability/about.html')


@login_required
def calendar_filter(request, year, month):
    if (int(month)>12):
        return HttpResponseRedirect("/ce_availability/calendar/")
    hours=0,5
    first_day_of_week, last_day = monthrange(int(year), int(month))
    monthname=month_name[int(month)]
    #print("MONTH=" + month)
    if(month==str(1)):
        prev_url="/ce_availability/calendar/"+str(int(year)-1)+"/12"
        next_url="/ce_availability/calendar/"+year+"/"+str(int(month)+1)+"/"
    elif(month==str(12)):
        prev_url="/ce_availability/calendar/"+year+"/"+str(int(month)-1)+"/"
        next_url="/ce_availability/calendar/"+str(int(year)+1)+"/1"
    else:
        prev_url="/ce_availability/calendar/"+year+"/"+str(int(month)-1)+"/"
        next_url="/ce_availability/calendar/"+year+"/"+str(int(month)+1)+"/"
    print("URLS: " + prev_url + ", " + next_url)
    month_range = range(1, last_day + 1)
    day_of_week = {}
    day_week = first_day_of_week
    #F=festiu, L=laborable, I=intensiva
    for day in month_range:
        if(5==day_week or day_week==6):
            day_of_week[day]="F"
        elif(day_week==4):
            day_of_week[day]="I"
        else:
            day_of_week[day]="L"
        if (day_week==6):
            day_week=0
        else:
            day_week = day_week + 1
    #print(day_of_week)
    user=request.user
    user_type=getUserType(user)

    if user_type=='CE':
       manager_id=user.employee.manager.id
       employees=User.objects.filter(id=user.id)
    if user_type=='SDM':
       manager_id=user.id
       #ce='All'
       employees = User.objects.filter(groups__name='CE').filter(employee__manager=manager_id).order_by('last_name')
    data={}
    for employee in employees:
        data[employee.username]={}
        #print(employee)
        registers=Register.objects.filter(start_date__year=year).filter(start_date__month=month).filter(user_id=employee)
        #print(str(registers))
        for day in month_range:
            data[employee.username][day]={}
            hours=0
            registers_day=registers.filter(start_date__day=day)
            #print(str(day) + ", " + str(registers_day))
            for r in registers_day:
                #print(r)
                hours = hours + r.hours
            #print(employee.username + ", " + str(day) + ", " + str(hours))
            data[employee.username][day]={hours}
            #print(data[employee.username][day])
    #print(data)
    sum_hours={}
    for usr, value in data.items():
        sum_hours[usr]=0
        for day, hours in value.items():
            for h in hours:
                #print(str(usr) + ", " +str(day)+", " + str(h))
                sum_hours[usr]+=h 
    #print(sum_hours)

    return render(request, 'ce_availability/calendar.html', {'data': data, 'day_of_week': day_of_week,'employees': employees, 'year':year,'month': month, 'monthname':monthname,'first_day_of_week': first_day_of_week, 'month_range':month_range ,'hours':hours, 'next_url':next_url, 'prev_url': prev_url, 'sum_hours': sum_hours})

@login_required
def calendar(request):
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    return HttpResponseRedirect("/ce_availability/calendar/" + str(currentYear) + "/" + str(currentMonth))


@login_required
def list(request):
    user=request.user
    user_type=getUserType(user)
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    currentWeek = datetime.now().isocalendar()[1]

    print("INFO: VIEWS.list: usertype=" + user_type)

    if user_type=='CE':
       manager_id=user.employee.manager.id
       ce=user.id
    if user_type=='SDM':
       manager_id=user.id
       ce='All'
    unavailability='All'
    category='All'
    return HttpResponseRedirect("/ce_availability/list/filter/" + str(ce) + "/" + str(unavailability) + "/" + str(category) + "/" + str(currentYear) + "/" + str(currentMonth) + "/" + str(currentWeek))
    #return redirect("/ce_availability/list/filter/" + str(ce) + "/" + str(unavailability) + "/" + str(year) + "/" + str(month))

@login_required
def insert(request):

    user=request.user
    user_type=getUserType(user)
    print("INFO: VIEWS.list_filter: user.id=" + str(user.id) +", user_type=" + user_type)

    if user_type=='CE':
       ce_choices=[(choice.pk, choice.last_name  + ", " + choice.first_name) for choice in User.objects.filter(id=user.id)]
    if user_type=='SDM':
       manager_id=user.id
       ce_choices=[(choice.pk, choice.last_name + ", " + choice.first_name) for choice in User.objects.filter(groups__name='CE').filter(employee__manager=manager_id).order_by('last_name')]
    """
    for choice in ce_choices:
       print(choice)
    """
    register_id=0
    if request.method == "POST":
        form = RegisterForm(register_id, ce_choices, request.POST)
        ce = form['user'].value()
        print("INFO: VIEWS.list_filter: ce=" + str(ce))
        if form.is_valid():
            register = form.save(commit=False)
            register.user_id = int(ce)
            register.save()
            result=True
            return render(request, 'ce_availability/insert_post.html', {'result':result, 'id': register.id})
    else:
        #form = RegisterForm(ce_choices, request.POST)
        form = RegisterForm(register_id, ce_choices)
    return render(request, 'ce_availability/insert.html', {'form': form})

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
def register_details(request, pk):
    user=request.user
    user_type=getUserType(user)
    print("INFO: VIEWS.register_details: user.id=" + str(user.id) +", user_type=" + user_type)

    if user_type=='CE':
       ce_choices=[(choice.pk, choice.last_name  + ", " + choice.first_name) for choice in User.objects.filter(id=user.id)]
    if user_type=='SDM':
       manager_id=user.id
       ce_choices=[(choice.pk, choice.last_name  + ", " + choice.first_name) for choice in User.objects.filter(groups__name='CE').filter(employee__manager=manager_id).order_by('last_name')]
    """
    for choice in ce_choices:
       print(choice)
    """
    register = get_object_or_404(Register, pk=pk)
    register_id=register.id
    #user=register.user_id
    if request.method == "POST":
        print("INFO: VIEWS.register_details: POST")
        form = RegisterForm(register_id, ce_choices, request.POST, instance=register)
        #print("INFO: VIEWS.register_details: form=" +str(form))
        if form.is_valid():
            print("INFO: VIEWS.register_details: FORM_IS_VALID")
            #register.delete()
            register = form.save(commit=False)
            #register.user_id = user
            register.save()
            result=True
            #return redirect(request.session['url'])
            return render(request, 'ce_availability/update_post.html', {'result':result, 'id': register.id})
            
    else:
        form = RegisterForm(register_id, ce_choices, instance=register)
    return render(request, 'ce_availability/register_details.html', {'form': form, 'register': register})

@login_required
def register_delete(request, pk):
    register = get_object_or_404(Register, pk=pk)
    id = register.id
    register.delete()
    result=True
    return render(request, 'ce_availability/delete_post.html', {'result':result, 'id': id})
    #return redirect(request.session['url'])

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
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
