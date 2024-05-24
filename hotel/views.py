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
    req_list = json.loads(serialize('json', request.get_request(room_id, request.start_time,request.start_time)))
    ret = [[{'room_id' : room_id, 'fee' : fee}], req_list]
    return JsonResponse(ret, safe=False)



# ============静态变量===========

class RoomCounter:  # 分配房间号
    num = 0
    dic = {}


class RoomInfo:  # Room->字典
    dic = {
        "target_temp": "--",
        "init_temp": "--",
        "current_temp": "--",
        "fan_speed": "--",
        "fee": 0,
        "room_id": 0
    }

    def __init__(self, room):
        self.dic["target_temp"] = room.target_temp
        self.dic["init_temp"] = room.init_temp
        self.dic["current_temp"] = int(room.current_temp)
        self.dic["fan_speed"] = speed_ch[room.fan_speed]
        self.dic["fee"] = int(room.fee)
        self.dic["room_id"] = room.room_id
class RoomBuffer:  # 房间数据缓存
    on_flag = [None, False, False, False, False, False]
    target_temp = [0, 25, 25, 25, 25, 25]  # 不要用数组。。。。
    init_temp = [0, 32, 28, 30, 29, 35]

room_id = RoomCounter  # 房间号与session_id对应
room_info = RoomInfo # Room->字典
room_data = RoomBuffer # 房间数据缓存
speed_ch = ["", "高速", "中速", "低速"]
state_ch = ["", "服务中", "等待", "关机", "休眠"]

class RoomNumberExceededError(Exception):
    """Raised when the room number exceeds the limit"""
    pass


#====================
def get_room_id(request):
    s_id = request.session.session_key
    if s_id is None:
        request.session.create()
        s_id = request.session.session_key

    if s_id not in room_id.dic:
        room_id.num += 1
        if room_id.num > 5:
            raise RoomNumberExceededError("Room number has exceeded the limit")
        else:
            room_id.dic[s_id] = room_id.num
            return room_id.dic[s_id]
    else:
        return room_id.dic[s_id]

def client_off(request):  # 第一次访问客户端界面、# 开机
    room_id = get_room_id(request)
    room = Room.get_room(room_id)
    if room.on:
        room.turn_off()


def client_on(request):
    pass
def power(request):  # 客户端-电源键
    pass
def change_high(request):  # 客户端-高风
    pass
def change_mid(request):  # 中速
    pass
def change_low(request):  # 低速
    pass
def change_up(request):  # 升高温度
    pass
def change_down(request):  # 降低温度
    pass
#====================
