from django.urls import path
from . import views

app_name = 'activitylog'

urlpatterns = [
    path('', views.activity_log_list, name='activity_log_list'),
]