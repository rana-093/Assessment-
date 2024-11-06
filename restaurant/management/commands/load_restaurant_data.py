import json
import sys
from django.core.management.base import BaseCommand
from restaurant.models import Restaurant, MenuItem, OpeningHour
import re
from datetime import datetime, timedelta

DAYS_OF_WEEK = ['Mon', 'Tues', 'Weds', 'Thurs', 'Fri', 'Sat', 'Sun']

DAY_ALIASES = {
    "Thu": "Thurs",
    "Tue": "Tues",
    "Wed": "Weds",
}

def normalize_day(day):
    return DAY_ALIASES.get(day, day)


def parse_time(time_str):
    time_str = time_str.strip()
    if ':' not in time_str:
        time_str = time_str.replace(' ', ':00 ')
    return datetime.strptime(time_str.strip(), "%I:%M %p").strftime("%H:%M")

def parse_opening_hours_str(opening_hours_str: str):
    entries = re.split(r' / ', opening_hours_str)
    opening_hours_data = []

    for entry in entries:
        words = entry.split()
        day_part = []
        time_part = []

        for word in words:
            if any(char.isdigit() for char in word):
                time_part = words[words.index(word):]
                break
            else:
                day_part.append(word)

        days_str = " ".join(day_part).strip(",")
        time_str = " ".join(time_part)

        days = [day.strip() for day in days_str.split(',')]
        expanded_days = []
        # print(f'days_str: {days_str}, time_str: {time_str}')
        for day in days:
            if '-' in day:
                start_day, end_day = day.split('-')
                start_index = DAYS_OF_WEEK.index(normalize_day(start_day.strip()))
                end_index = DAYS_OF_WEEK.index(normalize_day(end_day.strip()))
                expanded_days.extend(DAYS_OF_WEEK[start_index:end_index + 1])
            else:
                expanded_days.append(normalize_day(day.strip()))

        if ' - ' in time_str:
            opening_time_str, closing_time_str = [t.strip() for t in time_str.split(' - ')]
            opening_time = parse_time(opening_time_str)
            closing_time = parse_time(closing_time_str)

            if closing_time < opening_time: # midnight crossing case, break it into 2 intervals
                interval_1 = (opening_time, datetime.strptime("23:59", "%H:%M").time())
                interval_2 = (datetime.strptime("00:00", "%H:%M").time(), closing_time)
                for day in expanded_days:
                    index = DAYS_OF_WEEK.index(day)
                    next_day = DAYS_OF_WEEK[(index + 1) % len(DAYS_OF_WEEK)]
                    opening_hours_data.append((day, interval_1[0], interval_1[1]))
                    opening_hours_data.append((next_day, interval_2[0], interval_2[1]))
            else :
                for day in expanded_days:
                    opening_hours_data.append((day, opening_time, closing_time))

    return opening_hours_data


class Command(BaseCommand):
    help = "Load the restaurant JSON datas into the database."

    def handle(self, *args, **kwargs):
        self.stdout.write("Loading Restaurants data...\n", ending="")
        sys.stdout.flush()
        with open('restaurant_with_menu.json', 'r') as file:
            restaurant_data = json.load(file)
        for data in restaurant_data:
            restaurant, created = Restaurant.objects.get_or_create(
                name=data['restaurantName'],
                defaults={
                    'name': data['restaurantName'],
                    'cash_balance': data['cashBalance']
                }
            )

            if not created:
                restaurant.menu_items.all().delete()

            for item in data['menu']:
                MenuItem.objects.get_or_create(
                    restaurant=restaurant,
                    name=item['dishName'],
                    defaults={'price': item['price']}
                )

            opening_hours = parse_opening_hours_str(opening_hours_str=data['openingHours'])
            for opening_hour in opening_hours:
                OpeningHour.objects.get_or_create(
                    restaurant=restaurant,
                    day=opening_hour[0],
                    opening_time=opening_hour[1],
                    defaults={'closing_time': opening_hour[2]}
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded restaurant data'))
