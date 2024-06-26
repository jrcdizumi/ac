"""
URL configuration for ac project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hotel.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('monitor/', get_monitor_page, name='monitor'),
    path('refresh_monitor/', refresh_monitor, name='refresh_monitor'),
    path('monitor_manage/', monitor_manage, name='monitor_manage'),
    path('monitor_change/', monitor_change, name='monitor_change'),
    
    path('front/', get_front_page, name='front'),
    path('check_in/', check_in),
    path('check_out/', check_out),

    # 默认
    # path('client/<int:room_id>/', client_view, name='client'),
    path('off/', client_off,name='off'),
    path('on/', client_on,name='on'),
    # 客户端按钮
    path('power/', power),
    path('high/', change_high),
    # path('mid/', change_mid),
    path('low/', change_low),
    path('up/', change_up),
    path('down/', change_down),
    path('get_fee/', get_fee),
    path('get_status/', get_status),

    # 管理员和前台入口
    path('', entry, name='entry'),
]
