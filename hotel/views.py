from django.shortcuts import render
from hotel.models import Room
from hotel.models import Request
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.core.serializers import serialize
from django.forms.models import model_to_dict
import json


# Create your views here.
#获取监控页面
def get_monitor_page(request):
    rooms = Room.objects.all()
    return render(request, 'monitor.html', {'rooms': rooms})


#刷新监控数据
def refresh_monitor(request):  #监控界面获取数据
    rooms = Room.objects.all()
    data = []
    for room in rooms:
        data.append({
            'room_id': room.room_id,
            'current_temp': room.current_temp,
            'fan_speed': room.get_fan_speed_display(),
            'fee': room.fee,
            'on': room.on,
            'fee_rate': room.fee_rate,
        })
    return JsonResponse(data, safe=False)

#监控打开管理界面
def monitor_manage(request):
    if request.method == 'GET':
        room_id = request.GET.get('room_id')
        room = Room.get_room(room_id)
        room_dict = model_to_dict(room)
        return render(request, 'room_manage.html', room_dict)
    else:
        return JsonResponse({'status': 'invalid request method'})


def get_front_page(request):
    rooms = Room.objects.all()
    return render(request, 'front.html', {'rooms': rooms})


def check_in(request):
    request = Request()
    request.request_type = 5
    ret = []
    if (request.process()):
        ret.append({'room_id': request.room_id})
    else:
        ret.append({'room_id': -1})
    return JsonResponse(ret, safe=False)


def check_out(request):
    room_id = request.GET.get('id', '')
    print("id为" + room_id)
    request = Request()
    request.room_id = int(room_id)
    request.request_type = 6
    request.process()
    fee = request.fee
    start_time = request.start_time
    end_time = request.request_time
    req_list = json.loads(serialize('json', request.get_request(room_id, request.start_time, request.start_time)))
    print(req_list)
    ret = [[{'room_id': room_id, 'fee': fee, 'start_time': start_time, 'end_time': end_time}], req_list]
    return JsonResponse(ret, safe=False)


# ============静态变量===========
speed_ch = ["", "低速", "中速", "高速"]

class RoomCounter:  # 分配房间号
    num = 0
    dic = {}


class RoomInfo:  # Room->字典
    dic = {
        # "target_temp": "--",
        "current_temp": "--",
        "fan_speed": "--",
        "fee": 0,
        "room_id": 0
    }

    def __init__(self, room):
        # self.dic["target_temp"] = room.current_temp
        # self.dic["init_temp"] = RoomBuffer.init_temp[room.room_id]
        if room.current_temp is not None:
            self.dic["current_temp"] = str(int(room.current_temp))
        self.dic["fan_speed"] = speed_ch[room.fan_speed]
        self.dic["fee"] = int(room.fee)
        self.dic["room_id"] = room.room_id


room_Id = RoomCounter  # 房间号与session_id对应
room_info = RoomInfo  # 未开机时的房间信息
Work = Request() # 请求类

class RoomNumberExceededError(Exception):
    """Raised when the room number exceeds the limit"""
    pass


#====================
def get_room_id(request):
    s_id = request.session.session_key
    if s_id is None:
        request.session.create()
        s_id = request.session.session_key

    if s_id not in room_Id.dic:
        room_Id.num += 1
        if room_Id.num > 5:
            raise RoomNumberExceededError("Room number has exceeded the limit")
        else:
            room_Id.dic[s_id] = room_Id.num
            return room_Id.dic[s_id]
    else:
        return room_Id.dic[s_id]


def client_off(request):  # 第一次访问客户端界面、# 开机
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    if room.on:
        Work.turn_off(room_tid)
    return render(request, 'client-off.html', room_info.dic)


def client_on(request):
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    if not room.on:
        Work.turn_on(room_tid)
    print(RoomInfo(room).dic)
    return render(request, 'client-on.html', RoomInfo(room).dic)


def power(request):  # 客户端-电源键
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    # print("修改前: "+ str(room.on))
    if room.on:
        Work.turn_off(room_tid)
        # print(room.on)
        return HttpResponseRedirect('/')
    else:
        Work.turn_on(room_tid)
        return HttpResponseRedirect('/on/')


def change_high(request):  # 提高速度
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    Work.increase_speed(room_tid)
    data = {
        'fan_speed': speed_ch[room.fan_speed],
    }
    return JsonResponse(data)



# def change_mid(request):  # 中速
#     room_tid = get_room_id(request)
#     room = Room.get_room(room_tid)
#     if not room.on:
#         pass
#     else:
#         if room.set_speed(2):
#             data = {
#                 'fan_speed': speed_ch[room.fan_speed],
#             }
#             return JsonResponse(data)
#         else:
#             pass


def change_low(request):  # 降低速度
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    Work.decrease_speed(room_tid)
    data = {
        'fan_speed': speed_ch[room.fan_speed],
    }
    return JsonResponse(data)



def change_up(request):  # 升高温度
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    Work.increase_temp(room_tid)
    room.increase_temp()
    data = {
        'temp': room.current_temp,
    }
    return JsonResponse(data)


def change_down(request):  # 降低温度
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    Work.decrease_temp(room_tid)
    data = {
        'temp': room.current_temp,
    }
    return JsonResponse(data)


def get_fee(request):
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    if not room.on:
        data = {
            'fee': 0,
        }
        return JsonResponse(data)
    else:
        print("fee:"+str(room.fee))
        data = {
            'fee': round(room.fee, 2),
        }
        return JsonResponse(data)

def get_status(request):
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    data = {
        'status': room.on,
    }
    return JsonResponse(data)
#====================

