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
from django.middleware.csrf import get_token

def monitor_manage(request):
    if request.method == 'GET':
        room_id = request.GET.get('room_id')
        room = Room.get_room(room_id)
        room_dict = model_to_dict(room)

        # This will get or set the CSRF token
        csrftoken = get_token(request)

        # Create your response
        response = render(request, 'room_manage.html', room_dict)

        # Set the CSRF token in the cookie
        response.set_cookie('csrftoken', csrftoken)

        return response
    else:
        return JsonResponse({'status': 'invalid request method'})

#管路员修改
def monitor_change(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        room_id = int(data.get('room_id'))
        temp = float(data.get('temp'))
        fan_speed = int(data.get('fan_speed'))
        on = bool(data.get('on'))
        # print(room_id)
        # print(temp)
        # print(fan_speed)
        # print(on)
        room = Room.get_room(room_id)
        # print("================")
        # print(room.current_temp)
        # print(room.fee_rate)
        # print(room.on)
        if room is not None and room.is_occupied==False:
            room.set_temp(temp)
            room.set_speed(fan_speed)
            if on:
                room.on = True
            else:
                room.on = False
            room.save()  # Save changes to the database
            print("管理员修改成功")
            return JsonResponse({'status': 'success'})
        else:
            print("管理员修改失败")
            return JsonResponse({'status': 'failure'})
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
        if room_Id.num > 6:
            raise RoomNumberExceededError("Room number has exceeded the limit")
        else:
            room_Id.dic[s_id] = room_Id.num
            return room_Id.dic[s_id]
    else:
        return room_Id.dic[s_id]


def client_off(request):  # 第一次访问客户端界面、# 开机
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    Work = Request()
    if room.on:
        Work.turn_off(room_tid)
    return render(request, 'client-off.html', RoomInfo(room).dic)


def client_on(request):
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    Work = Request()
    if not room.on:
        Work.turn_on(room_tid)
    return render(request, 'client-on.html', RoomInfo(room).dic)


def power(request):  # 客户端-电源键
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    # print("修改前: "+ str(room.on))
    Work = Request()  # 请求类
    # if room.on:
    #     Work.turn_off(room_tid)
    #     return HttpResponseRedirect('/client/'+str(room_tid))
    # else:
    #     Work.turn_on(room_tid)
    #     return HttpResponseRedirect('/client/'+str(room_tid))
    if room.on:
        Work.turn_off(room_tid)
        return HttpResponseRedirect('/off')
    else:
        Work.turn_on(room_tid)
        if not room.is_occupied:
            return HttpResponseRedirect('/off')
        return HttpResponseRedirect('/on')


def change_high(request):  # 提高速度
    room_tid = get_room_id(request)
    Work = Request()  # 请求类
    Work.increase_speed(room_tid)
    room = Room.get_room(room_tid)
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
    Work = Request()  # 请求类
    Work.decrease_speed(room_tid)
    room = Room.get_room(room_tid)
    data = {
        'fan_speed': speed_ch[room.fan_speed],
    }
    return JsonResponse(data)



def change_up(request):  # 升高温度
    room_tid = get_room_id(request)
    Work = Request()  # 请求类
    Work.increase_temp(room_tid)
    room = Room.get_room(room_tid)
    data = {
        'temp': room.current_temp,
    }
    return JsonResponse(data)


def change_down(request):  # 降低温度
    room_tid = get_room_id(request)
    Work = Request()  # 请求类
    Work.decrease_temp(room_tid)
    room = Room.get_room(room_tid)
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
        data = {
            'fee': round(room.fee, 2),
        }
        return JsonResponse(data)

def get_status(request):
    room_tid = get_room_id(request)
    room = Room.get_room(room_tid)
    data = {
        'room_id': room.room_id,
        'status': room.on,
    }
    return JsonResponse(data)
#====================


# 入口函数
def entry(request):
    return render(request, 'entry.html')
def client_view(request, room_id):
    # room_tid = get_room_id(request)
    room_tid = room_id
    room = Room.get_room(room_tid)
    Work = Request()  # 请求类
    if room.on:
        return render(request, 'client-on.html', RoomInfo(room).dic)
    else :
        return render(request, 'client-off.html', RoomInfo(room).dic)
Room.calculate_fee()
