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

    # timer
    timer = None

    # 当前温度+1，但不大于30度
    def increase_temp(self):
        self.current_temp = min(self.current_temp + 1, 30)
        self.current_fee = self.calculate_fee()
        self.save()

    # 当前温度-1，但不小于16度
    def decrease_temp(self):
        self.current_temp = max(self.current_temp - 1, 16)
        self.current_fee = self.calculate_fee()
        self.save()

    # 风速+1，但不大于3
    def increase_speed(self):
        self.fan_speed = min(self.fan_speed + 1, 3)
        self.current_fee = self.calculate_fee()
        self.save()

    # 风速-1，但不小于1
    def decrease_speed(self):
        self.fan_speed = max(self.fan_speed - 1, 1)
        self.current_fee = self.calculate_fee()
        self.save()

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
            return False
        self.is_occupied = False
        fee = self.fee
        self.turn_off()
        self.fee = 0.0
        self.save()
        return fee

    # 空调开启时调用该函数，将空调设置为开启状态并开始计费，每秒钟费用+=fee_rate
    def turn_on(self):
        if self.on:
            return False
        self.on = True
        self.current_fee += self.fee_rate
        self.save()
        self.timer = threading.Timer(1, self.turn_on)
        self.timer.start()

    # 空调关闭时调用该函数，将空调设置为关闭状态并停止计费
    def turn_off(self):
        if not self.on:
            return False
        self.on = False
        self.save()
        self.timer.cancel()

    # 计算费率函数（温度越高，费率越低；风速越大，费率越高）
    def calculate_fee_rate(self):
        self.fee_rate = 1.0 * (31 - self.current_temp) * self.fan_speed / 40
        self.save()
        return self.fee_rate

    # 根据room_id获取对应房间
    @staticmethod
    def get_room(room_id):
        return Room.objects.get(room_id=room_id)

    # 创建n个房间，如果数据库中已经有房间，则不会创建
    @staticmethod
    def create_room(n=6):
        for i in range(1, n + 1):
            try:
                Room.objects.get(room_id=i)
            except ObjectDoesNotExist:
                Room.objects.create(room_id=i)

    # 查询第一个没人入住的房间，返回房间id
    @staticmethod
    def get_empty_room():
        for room in Room.objects.all():
            if not room.is_occupied:
                return room.room_id
        return 0


# 用户的所有请求，包括温度调整、风速调整、开关机、入住退房等
class Request(models.Model):
    REQUEST_CHOICE = [
        (0, 'turn on/off'),
        (1, 'increase temp'),
        (2, 'decrease temp'),
        (3, 'increase speed'),
        (4, 'decrease speed'),
        (5, 'check in'),
        (6, 'check out')
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
        if self.request_type == 0:
            if self.on:
                room.turn_off()
            else:
                room.turn_on()
        elif self.request_type == 1:
            room.increase_temp()
        elif self.request_type == 2:
            room.decrease_temp()
        elif self.request_type == 3:
            room.increase_speed()
        elif self.request_type == 4:
            room.decrease_speed()
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
            return Request.objects.filter(request_time__range=(left_time, right_time))
        if start_time is None:
            return Request.objects.filter(room_id=room_id, request_time__range=(left_time, right_time))
        return Request.objects.filter(room_id=room_id, start_time=start_time, request_time__range=(left_time, right_time))

    # 将年、月、日、时、分、秒格式化
    @staticmethod
    def time_to_timestamp(year, month, day, hour=0, minute=0, second=0):
        return datetime(year, month, day, hour, minute, second)

    # 从数据库中读取某个房间不同的入住时间的退房请求
    @staticmethod
    def get_check_out(room_id):
        if room_id == 0:
            return Request.objects.filter(request_type=6)
        return Request.objects.filter(room_id=room_id, request_type=6)
