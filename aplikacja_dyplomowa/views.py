from django.shortcuts import render
from django.http import HttpResponse
from .models import User

# Create your views here.


def index(request):

    context = {
        'users': User.objects.all
    }

    # return HttpResponse('Hello World!')
    return render(request, 'test.html', context)

