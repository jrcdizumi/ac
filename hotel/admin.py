from django.contrib import admin

# Register your models here.
from .models import Room
# Register your models here.


class RoomAdmin(admin.ModelAdmin):
    list_display = ['request_time', 'room_id', 'current_temp', 'target_temp', 'fan_speed', 'fee']


# 告诉管理页面，Scheduler对象需要被管理。
admin.site.register(Room, RoomAdmin)
