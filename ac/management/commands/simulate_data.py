from django.core.management.base import BaseCommand
from hotel.models import Room, Request
import random
import time


class Command(BaseCommand):
    help = 'Simulate data changes in Room model'

    def handle(self, *args, **options):
        fan_speeds = {'Low': 1, 'Medium': 2, 'High': 3}
        # 随机选择几个房间开启空调
        Room.calculate_fee()
        rooms = Room.objects.all()
        while True:
            for room in rooms:
                if random.random() > 0.5:
                    request = Request(room_id=room.room_id, request_type=0)
                    request.process()
            time.sleep(5)
            for room in rooms:
                if random.random() > 0.5:
                    request = Request(room_id=room.room_id, request_type=1)
                    request.process()
            time.sleep(5)
            for room in rooms:
                if random.random() > 0.5:
                    request = Request(room_id=room.room_id, request_type=2)
                    request.process()
            time.sleep(5)
            for room in rooms:
                if random.random() > 0.5:
                    request = Request(room_id=room.room_id, request_type=3)
                    request.process()
            time.sleep(5)
            for room in rooms:
                if random.random() > 0.5:
                    request = Request(room_id=room.room_id, request_type=4)
                    request.process()
            time.sleep(5)


