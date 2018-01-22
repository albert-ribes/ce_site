from django.shortcuts import render

# Create your views here.
from .models import Register, Unavailability
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
def list_filter(request, ce, unavailability, year, month, week):

    print("INFO: VIEWS.list_filter: ce=" + ce + ", unavailability=" + unavailability + ", year=" + year + ", month=" + month) 
    request.session['url'] = "/ce_availability/list/filter/" + str(ce) + "/" + str(unavailability) + "/" + str(year) + "/" + str(month) + "/"  + str(week) 
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
       ce_choices=[(choice.pk, choice) for choice in User.objects.filter(id=ce)]
    if user_type=='SDM':
       manager_id=user.id
       ce_choices=[(choice.pk, choice) for choice in User.objects.filter(groups__name='CE').filter(employee__manager=manager_id)]
       ce_choices= [('All', 'All')] + ce_choices
    
    for choice in ce_choices:
             print(choice)
    

    # If this is a POST request then process the Form data
    if request.method == "POST":
        # Create a form instance and populate it with data from the request (binding):
        form = ListFilterForm(request.user, ce_choices, request.POST)
         # Check if the form is valid:
        if form.is_valid():
            print("INFO: VIEWS.list: form.is_valid()")
            # process the data in form
            ce, unavailability, year, month, week = form.save(commit=False)
            if(year=='All' or month=='All'):
                week='All'
            if(year!=str(currentYear) or month!=str(currentMonth)):
                week='All'
            request.session['url'] = "/ce_availability/list/filter/" + str(ce) + "/" + str(unavailability) + "/" + str(year) + "/" + str(month + "/" + str(week))
            print("INFO: VIEWS.list: URL=" + request.session['url'])
            return HttpResponseRedirect("/ce_availability/list/filter/" + str(ce) + "/" + str(unavailability) + "/" + str(year) + "/" + str(month) + "/" +  str(week))
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
        if(user_type=='CE'):
            form = ListFilterForm(request.user, ce_choices, initial={'ce_selector': ce, 'year_selector': year, 'month_selector': month, 'unavailability_selector':unavailability, 'week_selector':week})
        else:
            form = ListFilterForm(request.user, ce_choices, initial={'ce_selector': ce, 'year_selector': year, 'month_selector': month, 'unavailability_selector':unavailability, 'week_selector':week})

    return render(request, 'ce_availability/list.html', {'registers': registers, 'form': form, 'hours': hours})

@login_required
def about(request):
    return render(request, 'ce_availability/about.html')


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
    return HttpResponseRedirect("/ce_availability/list/filter/" + str(ce) + "/" + str(unavailability) + "/" + str(currentYear) + "/" + str(currentMonth) + "/" + str(currentWeek))
    #return redirect("/ce_availability/list/filter/" + str(ce) + "/" + str(unavailability) + "/" + str(year) + "/" + str(month))

@login_required
def insert(request):

    user=request.user
    user_type=getUserType(user)
    print("INFO: VIEWS.list_filter: user.id=" + str(user.id) +", user_type=" + user_type)

    if user_type=='CE':
       ce_choices=[(choice.pk, choice) for choice in User.objects.filter(id=user.id)]
    if user_type=='SDM':
       manager_id=user.id
       ce_choices=[(choice.pk, choice) for choice in User.objects.filter(groups__name='CE').filter(employee__manager=manager_id)]
    """
    for choice in ce_choices:
       print(choice)
    """
    if request.method == "POST":
        form = RegisterForm(ce_choices, request.POST)
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
        form = RegisterForm(ce_choices)
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
       ce_choices=[(choice.pk, choice) for choice in User.objects.filter(id=user.id)]
    if user_type=='SDM':
       manager_id=user.id
       ce_choices=[(choice.pk, choice) for choice in User.objects.filter(groups__name='CE').filter(employee__manager=manager_id)]
    """
    for choice in ce_choices:
       print(choice)
    """
    register = get_object_or_404(Register, pk=pk)
    #user=register.user_id
    if request.method == "POST":
        print("INFO: VIEWS.register_details: POST")
        form = RegisterForm(ce_choices, request.POST, instance=register)
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
        form = RegisterForm(ce_choices, instance=register)
    return render(request, 'ce_availability/register_details.html', {'form': form, 'register': register})

@login_required
def register_delete(request, pk):
    register = get_object_or_404(Register, pk=pk)
    register.delete()
    return redirect('/ce_availability/list')

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
