from django.db import models
from django.utils import timezone
import threading
import django
import csv
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

# Create your models here.
class Room(models.Model):
    FAN_SPEED = [
        (3, "HIGH"),
        (2, "MIDDLE"),
        (1, "LOW"),
    ]

    room_id = models.IntegerField(verbose_name='房间号', default=1, primary_key=True)

    # 入住时间
    request_time = models.DateTimeField(verbose_name='入住时间', default=timezone.now)

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
        self.is_occupied = True
        self.save()

    # 退房时调用该函数，返回当前费用、自动关闭空调并将费用清零
    def checkout(self):
        self.is_occupied = False
        fee = self.fee
        self.turn_off()
        self.fee = 0.0
        self.save()
        return fee

    # 空调开启时调用该函数，将空调设置为开启状态并开始计费，每秒钟费用+=fee_rate
    def turn_on(self):
        self.on = True
        self.current_fee += self.fee_rate
        self.save()
        self.timer = threading.Timer(1, self.turn_on)
        self.timer.start()

    # 空调关闭时调用该函数，将空调设置为关闭状态并停止计费
    def turn_off(self):
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

# 用户的所有请求，包括温度调整、风速调整、开关机、入住退房等
class Request(models.Model):

    request_time = models.DateTimeField(verbose_name='请求时间', default=timezone.now)

    room_id = models.IntegerField(verbose_name='房间号', default=0)

    # 0: turn on/off; 1: increase temp; 2: decrease temp; 3: increase speed; 4: decrease speed
    request_type = models.IntegerField(verbose_name='请求类型', default=0)

    # 请求后的温度
    current_temp = models.FloatField(verbose_name='目标温度', default=25.0)

    # 请求后的风速
    fan_speed = models.IntegerField(verbose_name='目标风速', default=2)

    # 请求后的费用
    fee = models.FloatField(verbose_name='目标费用', default=0.0)

    # 请求后的费率
    fee_rate = models.FloatField(verbose_name='当前费率', default=0.3)

    # 请求后空调是否开启
    on = models.BooleanField(verbose_name='空调是否开启', default=False)

    # 根据room_id获取对应房间
    room = Room.get_room(room_id)

    current_temp = room.current_temp

    fan_speed = room.fan_speed

    fee = room.fee

    fee_rate = room.fee_rate

    on = room.on





