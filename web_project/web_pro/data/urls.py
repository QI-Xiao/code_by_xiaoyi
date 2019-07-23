from django.contrib import admin
from django.urls import path,include
from.views import test1

urlpatterns = [

    path('', test1),

]
