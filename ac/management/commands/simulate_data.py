from django.core.management.base import BaseCommand
from hotel.models import Room, Request
import random
import time


class Command(BaseCommand):
    help = 'Simulate data changes in Room model'

    def handle(self, *args, **options):
        fan_speeds = {'Low': 1, 'Medium': 2, 'High': 3}
        # 随机选择几个房间开启空调
        rooms = Room.objects.all()
        while True:
            for room in rooms:
                if random.random() > 0.5:
                    room.turn_on()
            time.sleep(5)
            for room in rooms:
                if random.random() > 0.5:
                    room.increase_speed()
            time.sleep(5)
            for room in rooms:
                if random.random() > 0.5:
                    room.decrease_speed()
            time.sleep(5)
            for room in rooms:
                if random.random() > 0.5:
                    room.increase_temp()
            time.sleep(5)
            for room in rooms:
                if random.random() > 0.5:
                    room.decrease_temp()
            for room in rooms:
                if random.random() > 0.5:
                    room.turn_off()
            time.sleep(5)


