from django.db import models
from django.utils import timezone
import threading
import django
import csv
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

# Create your models here.
class Room(models.Model):

    request_id = models.IntegerField(verbose_name="请求号", primary_key=True, default=0)

    # 请求发出时间
    request_time = models.DateTimeField(verbose_name="请求发出时间", default=django.utils.timezone.now)

    # 房间号，唯一表示房间
    room_id = models.IntegerField(verbose_name="房间号", default=0)

    # 当前温度
    current_temp = models.FloatField(verbose_name="当前温度", default=0.0)

    # 初始化温度
    init_temp = models.FloatField(verbose_name="初始化温度", default=0.0)

    # 目标温度
    target_temp = models.FloatField(verbose_name="目标温度", default=25.0)

    # 风速
    fan_speed = models.IntegerField(verbose_name='风速', choices=FAN_SPEED, default=2)

    # 房间状态
    state = models.IntegerField(verbose_name='服务状态', choices=ROOM_STATE, default=3)

    # 费率
    fee_rate = models.FloatField(verbose_name='费率', default=0.5)

    # 费用
    fee = models.FloatField(verbose_name='费用', default=0.0)

    # 当前服务时长
    serve_time = models.IntegerField(verbose_name='当前服务时长', default=0)

    # 当前等待时长
    wait_time = models.IntegerField(verbose_name='当前等待时长', default=0)

    # 操作类型
    operation = models.IntegerField(verbose_name='操作类型', choices=OPERATION_CHOICE, default=0)

    # 调度次数
    scheduling_num = models.IntegerField(verbose_name='调度次数', default=0)