from django.core.management.base import BaseCommand
from hotel.models import Room
import random
import time


class Command(BaseCommand):
    help = 'Simulate data changes in Room model'

    def handle(self, *args, **options):
        fan_speeds = {'Low': 1, 'Medium': 2, 'High': 3}
        while True:
            for room in Room.objects.all():
                room.current_temp = random.randint(16, 30)  # Random current_temp between 16.0 and 30.0
                room.fan_speed =random.randint(1, 3)
                room.fee += round(random.uniform(0.0, 5.0), 2)  # Randomly increase fee
                room.on = random.choice([True, False])  # Random on status
                room.fee_rate = round(random.uniform(0.0, 5.0), 2)  # Random fee_rate between 0.0 and 5.0
                room.save()
            time.sleep(3)
