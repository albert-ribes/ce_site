from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User, Group
from ce_availability.models import Register

from rest_framework import viewsets
from restapi.serializers import UserSerializer, GroupSerializer, RegisterSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class RegisterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows events to be viewed or edited.
    """
    queryset = Register.objects.all()
    serializer_class = RegisterSerializer



