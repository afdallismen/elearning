from django.shortcuts import render
from account.forms import *


def index(request):
    return render(request, 'main/index.html')
