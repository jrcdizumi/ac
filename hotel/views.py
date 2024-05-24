from django.shortcuts import render
from hotel.models import Room
from hotel.models import Request
from django.http import HttpResponse
from django.http import JsonResponse

# Create your views here.
#获取监控页面
def get_monitor_page(request):
    rooms = Room.objects.all()
    return render(request, 'monitor.html', {'rooms': rooms})

#刷新监控数据
def refresh_monitor(request):#监控界面获取数据
    rooms = Room.objects.all()
    data = []
    for room in rooms:
        data.append({
            'room_id': room.room_id,
            'current_temp': room.current_temp,
            'fan_speed': room.get_fan_speed_display(),
            'fee': room.fee,
            'on':room.on,
            'fee_rate':room.fee_rate,
        })
    return JsonResponse(data, safe=False)