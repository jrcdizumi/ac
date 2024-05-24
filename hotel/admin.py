from django.contrib import admin

# Register your models here.
from .models import Room, Request
# Register your models here.


class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_id', 'current_temp', 'fan_speed', 'fee', 'on', 'is_occupied', 'fee_rate', 'start_time']
    # 根据房间号排序
    ordering = ['room_id']


class RequestAdmin(admin.ModelAdmin):
    list_display = ['request_time', 'room_id', 'start_time', 'request_type', 'current_temp', 'fan_speed', 'fee', 'fee_rate', 'on']
    # 根据id排序
    ordering = ['id']


# 告诉管理页面对象需要被管理。
admin.site.register(Room, RoomAdmin)
admin.site.register(Request, RequestAdmin)

