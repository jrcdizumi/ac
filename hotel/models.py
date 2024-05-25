from django.db import models
from django.utils import timezone
import threading
import django
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from datetime import timedelta


# Create your models here.
class Room(models.Model):
    FAN_SPEED = [
        (3, "HIGH"),
        (2, "MIDDLE"),
        (1, "LOW")
    ]

    room_id = models.IntegerField(verbose_name='房间号', default=0, primary_key=True)

    # 入住时间
    start_time = models.DateTimeField(verbose_name='入住时间', default=timezone.now)

    # 当前温度
    current_temp = models.FloatField(verbose_name="当前温度", default=25.0)

    # 风速
    fan_speed = models.IntegerField(verbose_name='风速', choices=FAN_SPEED, default=2)

    # 费用
    fee = models.FloatField(verbose_name='费用', default=0.0)

    # 空调是否开启
    on = models.BooleanField(verbose_name='空调是否开启', default=False)

    # 房间是否有人入住
    is_occupied = models.BooleanField(verbose_name='房间是否有人入住', default=False)

    # 当前费率
    fee_rate = models.FloatField(verbose_name='当前费率', default=0.3)

    # 当前温度+1，但不大于30度
    def increase_temp(self):
        if not self.on or not self.is_occupied:
            return False
        if self.current_temp >= 30:
            return False
        self.current_temp = self.current_temp + 1
        self.fee_rate = self.calculate_fee_rate()
        self.save()
        return True

    # 当前温度-1，但不小于16度
    def decrease_temp(self):
        if not self.on or not self.is_occupied:
            return False
        if self.current_temp <= 16:
            return False
        self.current_temp = self.current_temp - 1
        self.fee_rate = self.calculate_fee_rate()
        self.save()
        return True

    # 修改温度为某个值，小于16度则修改为16度，大于30度则修改为30度
    def set_temp(self, temp):
        if temp < 16:
            temp = 16
        if temp > 30:
            temp = 30
        self.current_temp = temp
        self.fee_rate = self.calculate_fee_rate()
        self.save()
        return True

    # 风速+1，但不大于3
    def increase_speed(self):
        if not self.on or not self.is_occupied:
            return False
        if self.fan_speed >= 3:
            return False
        self.fan_speed = self.fan_speed + 1
        self.fee_rate = self.calculate_fee_rate()
        self.save()
        return True

    # 风速-1，但不小于1
    def decrease_speed(self):
        if not self.on or not self.is_occupied:
            return False
        if self.fan_speed <= 1:
            return False
        self.fan_speed = self.fan_speed - 1
        self.fee_rate = self.calculate_fee_rate()
        self.save()
        return True

    # 修改风速为某个值，小于1则修改为1，大于3则修改为3
    def set_speed(self, speed):
        if speed < 1:
            speed = 1
        if speed > 3:
            speed = 3
        self.fan_speed = speed
        self.fee_rate = self.calculate_fee_rate()
        self.save()
        return True

    # 入住时调用该函数，将房间设置为有人入住状态
    def checkin(self):
        if self.is_occupied:
            return False
        self.is_occupied = True
        self.fee = 0.0
        self.start_time = timezone.now()
        self.save()
        return True

    # 退房时调用该函数，返回当前费用、自动关闭空调并将费用清零
    def checkout(self):
        if not self.is_occupied:
            return -1
        self.turn_off()
        self.is_occupied = False
        fee = self.fee
        self.fee = 0.0
        self.save()
        return fee

    # 空调开启时调用该函数，将空调设置为开启状态并开始计费
    def turn_on(self):
        if self.on or not self.is_occupied:
            return False
        self.on = True
        self.save()
        return True

    # 空调关闭时调用该函数，将空调设置为关闭状态并停止计费
    def turn_off(self):
        if not self.on or not self.is_occupied:
            return False
        self.on = False
        self.save()
        return True

    # 计算费率函数（温度越高，费率越低；风速越大，费率越高）
    def calculate_fee_rate(self):
        self.fee_rate = 1.0 * (31 - self.current_temp) * self.fan_speed / 40
        self.save()
        return self.fee_rate

    # 根据room_id获取对应房间
    @staticmethod
    def get_room(room_id):
        return Room.objects.get(room_id=room_id)

    # 查询第一个没人入住的房间，返回房间id
    @staticmethod
    def get_empty_room():
        for room in Room.objects.all():
            if not room.is_occupied:
                return room.room_id
        return 0

    # 计费函数，每秒钟调用一次
    @staticmethod
    def calculate_fee():
        for room in Room.objects.all():
            if room.is_occupied and room.on:
                room.fee += room.fee_rate
                room.save()
        timer = threading.Timer(5, Room.calculate_fee)
        timer.start()


# 用户的所有请求，包括温度调整、风速调整、开关机、入住退房等
class Request(models.Model):
    REQUEST_CHOICE = [
        (0, 'turn on/off'),
        (1, 'increase temp'),
        (2, 'decrease temp'),
        (3, 'increase speed'),
        (4, 'decrease speed'),
        (5, 'check in'),
        (6, 'check out'),
        (7, 'set speed')
    ]
    FAN_SPEED = [
        (3, "HIGH"),
        (2, "MIDDLE"),
        (1, "LOW")
    ]

    request_time = models.DateTimeField(verbose_name='请求时间', default=timezone.now)

    room_id = models.IntegerField(verbose_name='房间号', default=0)

    # 入住时间，和room_id一起区分不同客人
    start_time = models.DateTimeField(verbose_name='入住时间', default=timezone.now)

    # 0: turn on/off; 1: increase temp; 2: decrease temp; 3: increase speed; 4: decrease speed
    request_type = models.IntegerField(verbose_name='请求类型', default=-1, choices=REQUEST_CHOICE)

    # 请求后的温度
    current_temp = models.FloatField(verbose_name='温度', default=25.0)

    # 请求后的风速
    fan_speed = models.IntegerField(verbose_name='风速', default=2, choices=FAN_SPEED)

    # 请求后的费用
    fee = models.FloatField(verbose_name='费用', default=0.0)

    # 请求后的费率
    fee_rate = models.FloatField(verbose_name='当前费率', default=0.3)

    # 请求后空调是否开启
    on = models.BooleanField(verbose_name='空调是否开启', default=False)

    def turn_on(self,room_id):
        self.request_type = 0
        self.room_id = room_id
        self.process()
    def turn_off(self,room_id):
        self.request_type = 0
        self.room_id = room_id
        self.process()
    def increase_temp(self,room_id):
        self.request_type = 1
        self.room_id = room_id
        self.process()
    def decrease_temp(self,room_id):
        self.request_type = 2
        self.room_id = room_id
        self.process()
    def increase_speed(self,room_id):
        self.request_type = 3
        self.room_id = room_id
        self.process()
    def decrease_speed(self,room_id):
        self.request_type = 4
        self.room_id = room_id
        self.process()


    # 根据房间号获取温度、风速、费用、费率以及空调状态并写入数据库
    def write(self):
        room = Room.get_room(self.room_id)
        self.start_time = room.start_time
        self.current_temp = room.current_temp
        self.fan_speed = room.fan_speed
        if self.request_type != 6:
            self.fee = room.fee
        self.fee_rate = room.fee_rate
        self.on = room.on
        self.save()

    # 根据请求类型处理请求并写入数据库,返回值为是否处理成功
    def process(self):
        if self.request_type == -1:
            return False
        if self.request_type == 5:
            self.room_id = Room.get_empty_room()
            if self.room_id == 0:
                return False
            else:
                room = Room.get_room(self.room_id)
                room.checkin()
        if self.room_id == 0:
            return False
        room = Room.get_room(self.room_id)
        if self.request_type == 6:
            fee = room.checkout()
            self.fee = fee
            if fee == -1:
                return False
        if self.request_type == 0:
            if room.on:
                if not room.turn_off():
                    return False
            else:
                if not room.turn_on():
                    return False
        elif self.request_type == 1:
            if not room.increase_temp():
                return False
        elif self.request_type == 2:
            if not room.decrease_temp():
                return False
        elif self.request_type == 3:
            if not room.increase_speed():
                return False
        elif self.request_type == 4:
            if not room.decrease_speed():
                return False
        self.write()
        return True

    # 根据房间号、入住时间和请求时间的区间获取请求列表
    @staticmethod
    def get_request(room_id=None, start_time=None, left_time=None, right_time=None):
        # 如果没有传入right_time,则默认为当前时间
        if right_time is None:
            right_time = timezone.now()
        # 如果没有传入left_time,则默认为right_time的前1天
        if left_time is None:
            left_time = right_time - timedelta(days=1)
        if room_id is None:
            return Request.objects.filter(request_time__range=(left_time - timedelta(seconds=1), right_time))
        if start_time is None:
            return Request.objects.filter(room_id=room_id, request_time__range=(left_time - timedelta(seconds=1), right_time))
        return Request.objects.filter(room_id=room_id, start_time=start_time, request_time__range=(left_time - timedelta(seconds=1), right_time))

    # 将年、月、日、时、分、秒格式化
    @staticmethod
    def time_to_timestamp(year, month, day, hour=0, minute=0, second=0):
        return datetime(year, month, day, hour, minute, second)

    # 从数据库中读取某个房间不同的入住时间的退房请求
    @staticmethod
    def get_check_out(room_id=None, left_time=None, right_time=None):
        if right_time is None:
            right_time = timezone.now()
        if left_time is None:
            left_time = right_time - timedelta(days=7)
        if room_id is None or room_id == 0:
            return Request.objects.filter(request_type=6, request_time__range=(left_time - timedelta(seconds=1), right_time))
        return Request.objects.filter(room_id=room_id, request_type=6, request_time__range=(left_time - timedelta(seconds=1), right_time))


