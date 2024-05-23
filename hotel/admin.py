from django.contrib import admin

# Register your models here.
from .models import Room, Request
# Register your models here.


# 告诉管理页面，Scheduler对象需要被管理。
admin.site.register(Room)
admin.site.register(Request)

