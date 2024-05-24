from django.shortcuts import render
from hotel.models import Room
from hotel.models import Request
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.serializers import serialize
import json

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

def get_front_page(request):
    rooms = Room.objects.all()
    return render(request, 'front.html', {'rooms': rooms})

def check_in(request):
    request = Request()
    request.request_type = 5
    ret = []
    if(request.process()):
        ret.append({'room_id' : request.room_id})
    else:
        ret.append({'room_id' : -1})
    return JsonResponse(ret, safe=False)



def check_out(request):
    room_id = request.GET.get('id', '')
    print("id为" + room_id)
    request = Request()
    request.room_id = int(room_id)
    request.request_type = 6
    request.process()
    fee = request.fee
    req_list = json.loads(serialize('json', request.get_request(room_id, request.start_time, request.start_time)))
    ret = [{'room_id' : room_id, 'fee' : fee}, req_list]
    return JsonResponse(ret, safe=False)