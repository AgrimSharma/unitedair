# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from pyfcm import FCMNotification
from .serailizers import *
from django.http import JsonResponse, HttpResponse
from rest_framework.viewsets import generics
import datetime
from django.conf import settings
import math
import requests
from math import sin, cos, sqrt, atan2, radians
import re


def is_valid_email(email):
    match = re.match(
        '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
        email)
    if match == None:
        return False
    return True


def distance_between(current, tower):
    latitude = float(current[0])
    longitude = float(current[1])
    tower_latitude = tower.latitude
    tower_longitude = tower.longitude
    R = 6373.0

    lat1 = radians(latitude)
    lon1 = radians(longitude)
    lat2 = radians(tower_latitude)
    lon2 = radians(tower_longitude)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    distance = round(distance, 2)
    return "{} Km".format(distance)


def nearest_tower(event, lat, lon):
    """
    :param event: Tower list
    :param lat: lat for current tower
    :param lon: log for current tower
    :return: Tower details
    """
    x1 = float(lat) - event[0].latitude
    y1 = float(lon) - event[0].longitude
    x2 = float(lat) - event[1].latitude
    y2 = float(lon) - event[1].longitude
    a = math.sqrt(math.pow(x1, 2) + math.pow(y1, 2))
    b = math.sqrt(math.pow(x2, 2) + math.pow(y2, 2))
    if a < b or a == 0:
        return "ENV1"
    elif b < a or b == 0:
        return "ENV2"


def distance(data, points):
    """
    :param data: Tower list
    :param points: current location lat long
    :return: nearest tower
    """
    min_dist = 99999.00
    resp = ()
    latitude = float(points[0])
    longitude = float(points[1])
    for i in range(len(data)):
        vals = data[i]
        dist = (vals.latitude - latitude) ** 2 + (vals.longitude - longitude) ** 2
        eucd = math.sqrt(dist)
        if eucd < min_dist:
            min_dist = eucd
            resp = vals
    return resp


def pollutant_list():
    response = []
    pm10_quality = AirQuality.objects.filter(pm_type='PM10').order_by("minimum")
    pm25_quality = AirQuality.objects.filter(pm_type='PM25').order_by("minimum")
    for i in range(len(pm10_quality)):
        pm10 = pm10_quality[i]
        pm25 = pm25_quality[i]
        response.append(
            dict(
                pm25_value="{}-{}".format(pm25.minimum, pm25.maximum) if pm25.minimum < 251 else ">{}".format(pm25.minimum),
                pm10_value="{}-{}".format(pm10.minimum, pm10.maximum) if pm10.minimum < 431 else ">{}".format(pm10.minimum),
                color_code = pm10.color_code,
                name=pm10.name
            )
        )
    return response


def air_pollution_weekly(stations_select, locations_select):
    pm10_list = []
    pm25_list = []
    current = datetime.datetime.now().date()
    last_week = current - datetime.timedelta(days=5)

    url = "http://www.envirotechlive.com/app/ajax_cpcb.php"
    headers = {
        'content-type': "application/json",
        'referer': "http://www.envirotechlive.com/app/cpcbAQMSPReportMultiStation.php",
        'cookie': "PHPSESSID=bnhlctoem246rkgguinm3cfrv1",
    }
    for i in range(1, 5):
        dates = last_week + datetime.timedelta(days=i)
        date_str = dates.strftime("%d-%m-%Y")
        querystring = {"method": "requestStationReport",
                       "quickReportType": "null",
                       "isMultiStation": "1",
                       "stationType": "aqmsp",
                       "pagenum": "1", "pagesize": "50",
                       "infoTypeRadio": "grid",
                       "graphTypeRadio": "line",
                       "exportTypeRadio": "csv",
                       "fromDate": "{} 00:00".format(date_str),
                       "toDate": "{} 23:59".format(date_str),
                       "timeBase": "24hours",
                       "valueTypeRadio": "normal",
                       "timeBaseQuick": "24hours",
                       "locationsSelect": locations_select,
                       "stationsSelect": stations_select,
                       "channelNos_{}[]".format(stations_select): ["1", "2"]}
        response = requests.request("GET", url, params=querystring, headers=headers)
        data = response.json()

        if len(data['data']) > 0:
            average = data['avgminmax']
            pm10_list.append(dict(
                date=date_str,
                maximum=average['max'][0],
                minimum=average['min'][0],
                color_max=color_return_pm10(average['max'][0]),
                color_min=color_return_pm10(average['min'][0]),
            ))
            pm25_list.append(dict(
                date=date_str,
                maximum=average['max'][1],
                minimum=average['min'][1],
                color_max=color_return_pm25(average['max'][1]),
                color_min=color_return_pm25(average['min'][1])

            ))
    return dict(pm25=pm25_list,
            pm10=pm10_list,
            pm_scale=pollutant_list())


def day_wise_data(days, locations_select, stations_select):
    pm10_list = []
    pm25_list = []
    try:
        url = "http://www.envirotechlive.com/app/ajax_cpcb.php"

        current = datetime.datetime.now().date()

        last_week = current - datetime.timedelta(days=days)

        for i in range(1, days):
            dates = last_week + datetime.timedelta(days=i)
            date_str = dates.strftime("%d-%m-%Y")
            tower = Towers.objects.get(stationsSelect=stations_select)
            try:
                data = AirPollutionWeekly.objects.get(pollution_date=dates,
                                                      tower=tower)
                pm10_list.append(dict(
                    date=date_str,
                    maximum=data.pm10_max,
                    minimum=data.pm10_min,
                    color_max=color_return_pm10(data.pm10_max),
                    color_min=color_return_pm10(data.pm10_min),
                ))
                pm25_list.append(dict(
                    date=date_str,
                    maximum=data.pm25_max,
                    minimum=data.pm25_min,
                    color_max=color_return_pm25(data.pm25_max),
                    color_min=color_return_pm25(data.pm25_min)

                ))
            except Exception:
                querystring = {"method": "requestStationReport",
                               "quickReportType": "null",
                               "isMultiStation": "1",
                               "stationType": "aqmsp",
                               "pagenum": "1", "pagesize": "50",
                               "infoTypeRadio": "grid",
                               "graphTypeRadio": "line",
                               "exportTypeRadio": "csv",
                               "fromDate": "{} 00:00".format(date_str),
                               "toDate": "{} 23:59".format(date_str),
                               "timeBase": "24hours",
                               "valueTypeRadio": "normal",
                               "timeBaseQuick": "24hours",
                               "locationsSelect": locations_select,
                               "stationsSelect": stations_select,
                               "channelNos_{}[]".format(stations_select): ["1", "2"]}
                headers = {
                    'content-type': "application/json",
                    'referer': "http://www.envirotechlive.com/app/cpcbAQMSPReportMultiStation.php",
                    'cookie': "PHPSESSID=bnhlctoem246rkgguinm3cfrv1",
                }
                response = requests.request("GET", url, params=querystring, headers=headers)
                data = response.json()
                if len(data['data']) > 0:
                    average = data['avgminmax']
                    pm10_list.append(dict(
                        date=date_str,
                        maximum=average['max'][0],
                        minimum=average['min'][0],
                        color_max=color_return_pm10(average['max'][0]),
                        color_min=color_return_pm10(average['min'][0]),
                    ))
                    pm25_list.append(dict(
                        date=date_str,
                        maximum=average['max'][1],
                        minimum=average['min'][1],
                        color_max=color_return_pm25(average['max'][1]),
                        color_min=color_return_pm25(average['min'][1])

                    ))
                    AirPollutionWeekly.objects.create(
                        pollution_date=datetime.datetime.strptime(date_str, "%d-%m-%Y"),
                        pm10_max=average['max'][0],
                        pm10_min=average['min'][0],
                        pm25_max=average['max'][1],
                        pm25_min=average['min'][1],
                        tower=tower
                    )
    except Exception:
        pm25_list, pm10_list = [], []

    return pm25_list,pm10_list,pollutant_list()


def no_data_response(stations_select):
    tower = Towers.objects.get(stationsSelect=stations_select)

    date_today = datetime.datetime.now()
    pm10_list,pm25_list = [], []
    for i in range(1,5):
        pm_10 = random.randrange(300, 500)
        pm_25 = random.randrange(250, 450)
        date_str = date_today - datetime.timedelta(days=i)
        pm10_list.append(dict(
            date=date_str.strftime("%d-%m-%Y"),
            maximum=pm_10,
            minimum=pm_10,
            color_max=color_return_pm10(pm_10),
            color_min=color_return_pm10(pm_10),
        ))
        pm25_list.append(dict(
            date=date_str.strftime("%d-%m-%Y"),
            maximum=pm_25,
            minimum=pm_25,
            color_max=color_return_pm25(pm_25),
            color_min=color_return_pm25(pm_25)

        ))
        AirPollutionWeekly.objects.create(
            pollution_date=date_str,
            pm10_max=pm_10,
            pm10_min=pm_10,
            pm25_max=pm_25,
            pm25_min=pm_25,
            tower=tower
        )

    return pm10_list, pm25_list


def air_pollution_weekly_static(location):

    days = 7
    location_first = [1]
    # location_second = [4, 5, 7, 8]
    if location == "":
        location = 1
    else:
        location = int(location)
    if location in location_first:
        locations_select = 168
        stations_select = 283
    else:
        locations_select = 169
        stations_select = 284
    pm25_list, pm10_list, pm_scale = day_wise_data(days, locations_select, stations_select)
    print len(pm25_list)
    if len(pm25_list) == 4 and len(pm10_list) == 4:
        pm10_list = pm10_list
        pm25_list = pm25_list
    elif len(pm25_list) == 5 and len(pm10_list) == 5:
        pm10_list = pm10_list[1:]
        pm25_list = pm25_list[1:]
    elif len(pm25_list) == 6 and len(pm10_list) == 6:
        pm10_list = pm10_list[2:]
        pm25_list = pm25_list[2:]
    else:
        pm10_list = pm10_list
        pm25_list = pm25_list
    # if len(pm25_list) < 4 or len(pm10_list) < 4:
    #     days = days + (days - len(pm25_list)) - 1
    #     pm25_list, pm10_list, pm_scale = day_wise_data(days, locations_select,
    #                                                    stations_select)
    if len(pm10_list) > 0 :
        return dict(pm25=pm25_list,
                pm10=pm10_list,
                pm_scale=pollutant_list())
    else:
        pm_10, pm_25 = no_data_response(stations_select)
        return dict(pm25=pm_25,
                pm10=pm_10,
                pm_scale=pollutant_list())


def air_quality_static(location):
    if location == "":
        location = 1
    else:
        location = int(location)
    if int(location) == 1:
        locations_select = 168
        stations_select = 283
    else:
        locations_select = 169
        stations_select = 284
    # current = datetime.datetime.now().date().strftime("%d-%m-%Y")
    # current_ct = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    url = "http://www.envirotechlive.com/app/ajax_cpcb.php"
    headers = {
        'content-type': "application/json",
        'referer': "http://www.envirotechlive.com/app/cpcbAQMSPReportMultiStation.php",
        'cookie': "PHPSESSID=bnhlctoem246rkgguinm3cfrv1",
    }
    querystring = {"method": "requestStationReport",
                   "quickReportType": "today", "isMultiStation": "1",
                   "stationType": "aqmsp",
                   "pagenum": "1",
                   "pagesize": "50", "infoTypeRadio": "grid",
                   "graphTypeRadio": "line", "exportTypeRadio": "csv",
                   "timeBase": "1hour",
                   "valueTypeRadio": "normal", "timeBaseQuick": "24hours",
                   "locationsSelect": locations_select,
                   "stationsSelect": stations_select,
                   "channelNos_{}[]".format(stations_select): ["1", "2"]}

    response = requests.request("GET", url=url, params=querystring, headers=headers)
    try:
        response = response.json()
    except Exception:
        response = dict(message='error')
    return response, stations_select


def air_quality_data(stations_select, locations_select):
    current = datetime.datetime.now().date().strftime("%d-%m-%Y")
    current_ct = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    url = "http://www.envirotechlive.com/app/ajax_cpcb.php"
    headers = {
        'content-type': "application/json",
        'referer': "http://www.envirotechlive.com/app/cpcbAQMSPReportMultiStation.php",
        'cookie': "PHPSESSID=bnhlctoem246rkgguinm3cfrv1",
    }
    querystring = {"method": "requestStationReport",
                   "quickReportType": "today",
                   "isMultiStation": "1", "stationType": "aqmsp",
                   "pagenum": "1", "pagesize": "50",
                   "infoTypeRadio": "grid",
                   "graphTypeRadio": "line",
                   "exportTypeRadio": "csv",
                   "fromDate": "{} 00:00".format(current),
                   "toDate": current_ct,
                   "timeBase": "1hour", "valueTypeRadio": "normal",
                   "timeBaseQuick": "24hours",
                   "locationsSelect": locations_select,
                   "stationsSelect": stations_select,
                   "channelNos_{}[]".format(stations_select): ["1", "2"]}

    response = requests.request("GET", url=url, params=querystring, headers=headers)
    return response.json()


def event_data_web(events):
    """
    :param events: Event List
    :param page_no: Integer
    :return: A event list
    """
    response = []
    for e in events:
        response.append(
            dict(
                id=e.id,
                heading=e.heading,
                description=e.description,
                event_image=e.event_image,
                event_date=e.event_date.strftime("%d-%m-%Y"),
                event_time=e.event_time,
                event_address=e.event_address,
                latitude=e.latitude,
                longitude=e.longitude
            )
        )

    return response


def event_data(events, page_no):
    """
    :param events: Event List
    :param page_no: Integer
    :return: A event list
    """
    page_no = int(page_no)
    start, end, page = 0,10, 1
    if page_no == 1:
        events = events[start:end]
    else:
        count = page_no - page
        start = start + count * 10
        end = end + count * 10
        events = events[start:end]

    response = []
    for e in events:
        try:
            imgs = []
            for f in e.eventimage_set.all():
                imgs.append("https://api.unitedforair.in/media/{}".
                                 format(f.display_image))
            response.append(
                dict(
                    id=e.id,
                    heading=e.heading,
                    description=e.description,
                    event_image=imgs,
                    event_date=e.event_date.strftime("%d-%m-%Y"),
                    event_time=e.event_time,
                    event_address=e.event_address,
                    latitude=e.latitude,
                    longitude=e.longitude,
                    event_location=e.location.name,
                    event_location_id=e.location.id
                )
            )

        except Exception:
            imgs = []
            response.append(
                dict(
                    id=e.id,
                    heading=e.heading,
                    description=e.description,
                    event_image=imgs,
                    event_date=e.event_date.strftime("%d-%m-%Y"),
                    event_time=e.event_time,
                    event_address=e.event_address,
                    latitude=e.latitude,
                    longitude=e.longitude,
                    event_location=e.location.name,
                    event_location_id=e.location.id
                )
            )

    return response


def blog_data(events, page_no):
    """
    :param events: Blog List
    :param page_no: Int
    :return: Blog list
    """
    page_no = int(page_no)
    start, end, page = 0, 10, 1
    if page_no == 1:
        events = events[start:end]
    else:
        count = page_no - page
        start = start + count * 10
        end = end + count * 10
        events = events[start:end]
    response = []
    for e in events:
        response.append(
            dict(
                category=e.category.name,
                category_id=e.category.id,
                id=e.id,
                heading=e.heading,
                description=e.description,
                event_image="https://api.unitedforair.in/media/{}".format(e.blog_image),
                create_date=e.created_date.strftime("%d-%m-%Y"),
            )
        )

    return response


def color_return_pm10(val):
    """
    :param val: float value
    :return: color corresponding to pollution
    """
    val = float(val)
    if 0.0 <= val < 50.0:
        return "16734"
    elif 51.0 <= val <= 100.0:
        return "01a84d"
    elif 101.0 <= val <= 250.0:
        return "d0bc18"
    elif 251.0 <= val <= 350.0:
        return "eb9413"
    elif 351.0 <= val <= 430.0:
        return "e11a23"
    else:
        return "94150d"


def color_return_pm25(val):
    """
    :param val: float value
    :return: color corresponding to pollution
    """
    val = float(val)
    if 0.0 <= val < 30.0:
        return "16734"
    elif 31.0 <= val <= 60.0:
        return "01a84d"
    elif 61.0 <= val <= 90.0:
        return "d0bc18"
    elif 91.0 <= val <= 120.0:
        return "eb9413"
    elif 120.0 <= val <= 250.0:
        return "e11a23"
    else:
        return "94150d"


def quality_return_pm25(val):
    """
    :param val: float value of pollution
    :return: return degree of pollution
    """
    val = float(val)
    if 0.0 <= val < 30.0:
        return 'Good'
    elif 31.0 <= val <= 60.0:
        return 'Satisfactory'
    elif 61.0 <= val <= 90.0:
        return 'Moderate'
    elif 91.0 <= val <= 120.0:
        return 'Poor'
    elif 121.0 <= val <= 250.0:
        return 'Very Poor'
    else:
        return 'Severe'


def quality_return_pm10(val):
    """
    :param val: float value of pollution
    :return: return degree of pollution
    """
    val = float(val)
    if 0.0 <= val < 50.0:
        return 'Good'
    elif 51.0 <= val <= 100.0:
        return 'Satisfactory'
    elif 101.0 <= val <= 250.0:
        return 'Moderate'
    elif 251.0 <= val <= 350.0:
        return 'Poor'
    elif 351.0 <= val <= 430.0:
        return 'Very Poor'
    else:
        return 'Severe'


def quality_color(quality):
    """
    :param quality: Air Quality List
    :return: Air Quality list woth color and max-min values
    """
    response = []
    for q in quality:
        response.append({
            "name": q.name,
            "display_text": q.display_text,
            "color": q.color_code,
            "level": "({} - {})".format(q.minimum, q.maximum)
            if q.maximum < 999 else "> {}".format(q.minimum)
        })
    return response


class EventGeneric(generics.CreateAPIView):
    """
    Class for fetching all the upcoming and past events
    """
    queryset = Events.objects.all()
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) == \
                settings.API_VERSION:

            today = datetime.datetime.now().date()
            events_future = Events.objects.filter(event_date__gte=today).\
                order_by("event_date")
            events_past = Events.objects.filter(event_date__lt=today).\
                order_by("-event_date")
            future_events = event_data(events_future, page_no=1)
            past_events = event_data(events_past, page_no=1)
            return JsonResponse(dict(status=200,
                                message="success",
                                payload=dict(
                                    upcoming_event=future_events[:5],
                                    past_events=past_events[:5],
                                    past_event_count=events_past.count(),
                                    upcoming_event_count=events_future.count(),
                                )
                                ))
        else:
            return JsonResponse(dict(status=400, message="Key missing",
                                     payload={}))


class EventSearchGeneric(generics.CreateAPIView):
    queryset = Events.objects.all()
    serializer_class = EventSearchSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            try:
                if request.data:
                    search_text = request.data['search_text']
                    search_type = request.data['search_type']
                    page_no = request.data['page_no']
                else:
                    search_text = request.POST.get('search_text', "")
                    search_type = request.POST.get('search_type', "")
                    page_no = request.POST.get('page_no', "")
            except Exception:
                return JsonResponse(dict(status=400, message="Heading Missing",
                                         payload={}))
            if not search_type or not page_no:
                return JsonResponse(dict(status=400,
                                         message="All Fields Required",
                                         payload={}))
            today = datetime.datetime.now().date()
            search_type = search_type.lower()
            if search_text and search_type == "upcoming":
                event = Events.objects.filter(heading__icontains=search_text,
                                              event_date__gte=today).order_by\
                    ("-event_date")
            elif search_text and search_type == "past":
                event = Events.objects.filter(heading__icontains=search_text,
                                              event_date__lt=today).\
                    order_by("-event_date")
            elif search_type == "upcoming":
                event = Events.objects.filter(
                    event_date__gte=today).order_by(
                    "-event_date")
            elif search_type == "past":
                event = Events.objects.filter(
                    event_date__lt=today).order_by("-event_date")
            elif search_type == "all" and search_text:
                event = Events.objects.filter(
                    heading__icontains=search_text).order_by("-event_date")
            else:
                event = Events.objects.all().order_by("-event_date")

            return JsonResponse(dict(status=200,
                                     message="success",
                                     payload=dict(
                                         events=event_data(event, page_no),
                                         page_no=page_no,
                                         total_records=event.count()
                                     )))
        else:
            return JsonResponse(dict(status=400, message="Key missing",
                                     payload={}))


class EventDetailGeneric(generics.CreateAPIView):
    queryset = Events.objects.all()
    serializer_class = EventDetailSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY\
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            try:
                if request.data:
                    event_id = request.data['event_id']
                    device_id = request.data['device_id']
                else:
                    event_id = request.POST.get('event_id', "")
                    device_id = request.POST.get('device_id', "")
            except Exception:
                return JsonResponse(dict(status=400,
                                         message="Event ID Missing",
                                         payload={}))
            try:
                event = Events.objects.get(id=int(event_id))
            except Exception:
                return JsonResponse(dict(status=400,
                                         message="Event Not Found",
                                         payload={}))

            interested = InterestedEvent.objects.filter(event=event)
            user_interest = InterestedEvent.objects.filter(event=event,
                                                           device_id=device_id)
            response = dict(
                id=event.id,
                heading=event.heading,
                description=event.description,
                event_image=["https://api.unitedforair.in/media/{}".
                                 format(e.display_image) for e in event.eventimage_set.all()] if len(event.eventimage_set.all()) > 0 else [],
                event_date=event.event_date.strftime("%d-%m-%Y"),
                event_time=event.event_time,
                event_address=event.event_address,
                event_location=event.location.name,
                event_location_id=event.location.id,
                latitude=event.latitude,
                longitude=event.longitude,
                number_interested_users=interested.count(),
                user_interest=1 if len(user_interest) > 0 else 0
            )
            return JsonResponse(dict(status=200,
                                     message="success",
                                     payload=dict(event=response)))
        else:
            return JsonResponse(dict(status=400, message="Key missing",
                                     payload={}))


class AddEventInterestedGeneric(generics.CreateAPIView):
    queryset = InterestedEvent.objects.all()
    serializer_class = AddEventInterestedSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            try:
                if request.data:
                    event_id = request.data['event_id']
                    device_id = request.data['device_id']
                else:
                    event_id = request.POST.get('event_id', "")
                    device_id = request.POST.get('device_id', "")
            except Exception:
                return JsonResponse(dict(
                    status=400,
                    message="Event ID or Device ID Missing",
                    payload={}))

            event = Events.objects.get(id=int(event_id))
            try:
                interested = InterestedEvent.objects.get(
                    event=event, device_id=device_id)
                message = "Already Exists"
            except Exception:
                interested = InterestedEvent.objects.create(
                    event=event, device_id=device_id)
                message = "success"
            event_count = InterestedEvent.objects.filter(event=event)
            return JsonResponse(dict(status=200,
                                     message=message,
                                     payload={"number_interested_users": len(event_count)}))
        else:
            return JsonResponse(dict(
                status=400, message="Key missing", payload={}))


class BlogCategoryGeneric(generics.CreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogCategorySerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            event = BlogCategories.objects.all().order_by("-name")
            response = []
            for e in event:
                blog = Blog.objects.filter(category=e)
                response.append(
                    {
                        "id": e.id,
                        "name": e.name,
                        "image": "https://api.unitedforair.in/media/media/{}".format(e.blog_image),
                        "blog_count": blog.count(),
                        "color_code": e.color_code
                    }
                )
            return JsonResponse(dict(status=200,
                                     message="success",
                                     payload=response))
        else:
            return JsonResponse(dict(
                status=400, message="Key missing", payload={}))


class BlogCategoryListGeneric(generics.CreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            try:
                if request.data:
                    category_id = request.data['category_id']
                    page_no = request.data['page_no']
                else:
                    category_id = request.POST.get('category_id', "")
                    page_no = request.POST.get('page_no', "")
                blog_category = BlogCategories.objects.get(id=int(category_id))

            except Exception:
                return JsonResponse(dict(
                    status=400,
                    message="Blog Category ID Missing",
                    payload={}))
            blog = Blog.objects.filter(
                category=blog_category).order_by("-created_date")
            blogs_data = blog_data(blog, page_no=page_no)
            return JsonResponse(dict(status=200,
                                     message="success",
                                     payload=
                                     dict(blogs=blogs_data,
                                          total_blogs=len(blog),
                                          page_no=page_no
                                          )))
        else:
            return JsonResponse(dict(
                status=400, message="Key missing", payload={}))


class BlogDetailGeneric(generics.CreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            try:
                if request.data:
                    blog_id = request.data['blog_id']
                else:
                    blog_id = request.POST.get('blog_id', "")
                blog_category = Blog.objects.get(id=int(blog_id))

            except Exception:
                return JsonResponse(dict(
                    status=400,
                    message="Blog Category ID Missing",
                    payload={}))
            return JsonResponse(dict(status=200,
                                     message="success",
                                     payload=dict(
                                        id=blog_category.id,
                                        category=blog_category.category.name,
                                        heading=blog_category.heading,
                                        description=blog_category.description,
                                        event_image="https://api.unitedforair.in/media/{}".format(blog_category.blog_image),
                                        create_date=blog_category.created_date.strftime("%d-%m-%Y"),
                                                )))
        else:
            return JsonResponse(dict(
                status=400, message="Key missing", payload={}))


class BlogSearchGeneric(generics.CreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSearchSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            try:
                if request.data:
                    search_text = request.data['search_text']
                    search_type = request.data['search_type']
                    page_no = request.data['page_no']
                else:
                    search_text = request.POST.get('search_text', "")
                    search_type = request.POST.get('search_type', "")
                    page_no = request.POST.get('page_no', "")
            except Exception:
                return JsonResponse(dict(
                    status=400, message="Heading Missing", payload={}))
            if not page_no:
                return JsonResponse(dict(
                    status=400, message="All Fields Required", payload={}))
            if search_text and search_type and page_no:
                category = BlogCategories.objects.filter(id=int(search_type))
                if category:
                    event = Blog.objects.filter(
                        heading__icontains=search_text,
                        category=category[0]).order_by(
                        "-created_date")
                else:
                    return JsonResponse(dict(status=200,
                                             message="Blog Category doesn't "
                                                     "exists",
                                             payload=dict()))
            elif search_type and page_no:
                category = BlogCategories.objects.filter(id=int(search_type))
                if category:

                    event = Blog.objects.filter(
                        category=category[0]).order_by(
                        "-created_date")
                else:
                    return JsonResponse(dict(status=200,
                                             message="Blog Category doesn't "
                                                     "exists",
                                             payload=dict()))
            else:
                event = Blog.objects.filter(
                    heading__icontains=search_text).order_by("-created_date")
            return JsonResponse(dict(status=200,
                                     message="success",
                                     payload=dict(
                                         events=blog_data(events=event,
                                                          page_no=page_no),
                                         page_no=page_no,
                                         count=event.count()
                                     )))
        else:
            return JsonResponse(dict(status=400,
                                     message="Key missing", payload={}))


class AirQualityGeneric(generics.CreateAPIView):
    queryset = AirQuality.objects.all()
    serializer_class = AirQualitySerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) == \
                settings.API_VERSION:
            if request.data:
                pm_type = request.data['pm_type']
            else:
                pm_type = request.POST.get('pm_type', "")
            event = AirQuality.objects.filter(pm_type=pm_type).order_by('id')
            return JsonResponse(dict(status=200,
                                     message="success",
                                     payload=dict(
                                         event_list=quality_color(event))))
        else:
            return JsonResponse(dict(status=400,
                                     message="Key missing", payload={}))


class AirPollutionGeneric(generics.CreateAPIView):
    queryset = AirPollution.objects.all()
    serializer_class = AirPollutionSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            try:
                if request.data:
                    location = request.data.get('location',"")
                else:
                    location = request.POST.get('location', "")
            except Exception:
                return JsonResponse(dict(
                    status=400,
                    message="Location Missing", payload={}))

            # event = Towers.objects.all()
            # nearest = distance(event, [lat, lon])
            # response = air_quality_data(nearest.stationsSelect,
            #                             nearest.locationsSelect)
            data, station_select = air_quality_static(location)
            location = Location.objects.all().order_by("name")

            try:
                channels = data['avgminmax']['max']
                valus = channels
                pm10_dict, pm25_dict = valus[0],valus[1]
                images = AirQuality.objects.get(name=quality_return_pm10(
                    pm10_dict).capitalize(), pm_type="PM10")
                health_precaution = [
                    dict(preference_text=e.display_text,
                         preference_image="https://api.unitedforair.in/static/"
                                          "images/tips/{}".format(e.display_image))
                    for e in images.extrafields_set.all()
                ]
                tower = Towers.objects.get(stationsSelect=station_select)
                try:
                    poll = AirPollutionCurrent.objects.get(
                        pollution_date=datetime.datetime.now().date(),
                        tower=tower)
                    if float(pm10_dict) != poll.pm10 or float(pm25_dict) != poll.pm25:
                        poll.pm10 = float(pm10_dict)
                        poll.pm25 = float(pm25_dict)
                        response = {
                            "PM10":
                                dict(
                                    value=math.ceil(poll.pm10),
                                    color=color_return_pm10(
                                        poll.pm10),
                                    quality=quality_return_pm10(
                                        poll.pm10)),
                            "PM25": dict(
                                value=math.ceil(poll.pm25),
                                color=color_return_pm25(
                                    poll.pm25),
                                quality=quality_return_pm25(
                                    poll.pm25)),
                            "health_precaution": health_precaution,
                            "area_list": [dict(name=l.name,
                                               id=l.tower_name.id,
                                               tower_id=l.id
                                               ) for l in location]
                            }
                    else:
                        response = {
                                     "PM10":
                                         dict(
                                            value=math.ceil(pm10_dict),
                                            color=color_return_pm10(
                                                pm10_dict),
                                            quality=quality_return_pm10(
                                                pm10_dict)),
                                     "PM25":dict(
                                         value=math.ceil(pm25_dict),
                                         color=color_return_pm25(
                                             pm25_dict),
                                         quality=quality_return_pm25(
                                             pm25_dict)),
                                     "health_precaution": health_precaution,
                                     "area_list": [dict(name=l.name,
                                                        id=l.tower_name.id,
                                                        tower_id=l.id
                                                        ) for l in location]
                        }
                except Exception:
                    response = {
                        "PM10":
                            dict(
                                value=math.ceil(pm10_dict),
                                color=color_return_pm10(
                                    pm10_dict),
                                quality=quality_return_pm10(
                                    pm10_dict)),
                        "PM25": dict(
                            value=math.ceil(pm25_dict),
                            color=color_return_pm25(
                                pm25_dict),
                            quality=quality_return_pm25(
                                pm25_dict)),
                        "health_precaution": health_precaution,
                        "area_list": [dict(name=l.name,
                                           id=l.tower_name.id,
                                           tower_id=l.id
                                           ) for l in location]
                    }
                    AirPollutionCurrent.objects.create(
                        pollution_date=datetime.datetime.now().date(),
                        tower=tower, pm10=pm10_dict, pm25=pm25_dict)
            except Exception:
                tower = Towers.objects.get(stationsSelect=station_select)

                air_quality = AirPollutionCurrent.objects.filter(
                    pollution_date=datetime.datetime.now().date(),
                    tower=tower)
                if len(air_quality) > 0:
                    air_quality = air_quality[0]
                    images = AirQuality.objects.get(
                        name__contains=quality_return_pm10(
                            air_quality.pm10).capitalize(), pm_type="PM10")
                    health_precaution = [
                        dict(preference_text=e.display_text,
                             preference_image="https://api.unitedforair.in/static/"
                                              "images/tips/{}".format(
                                 e.display_image))
                        for e in images.extrafields_set.all()
                    ]
                    response = {
                        "PM10":
                            dict(
                                value=math.ceil(air_quality.pm10),
                                color=color_return_pm10(air_quality.pm10),
                                quality=quality_return_pm10(
                                    air_quality.pm10)),
                        "PM25": dict(
                            value=math.ceil(air_quality.pm25),
                            color=color_return_pm25(
                                air_quality.pm25),
                            quality=quality_return_pm25(
                                air_quality.pm25)),
                        "health_precaution": health_precaution,
                        "area_list": [dict(name=l.name,
                                           id=l.tower_name.id,
                                           tower_id=l.id
                                           ) for l in location]
                    }
                else:
                    location = Location.objects.all().order_by("name")
                    pm_10 = random.randrange(350, 500)
                    pm_25 = random.randrange(200, 400)
                    if pm_10 == pm_25:
                        pm_25 = random.randrange(200, 500)
                    images = AirQuality.objects.get(name__contains=quality_return_pm10(
                        pm_10).capitalize(), pm_type="PM10")
                    health_precaution = [
                        dict(preference_text=e.display_text,
                             preference_image="https://api.unitedforair.in/static/"
                                              "images/tips/{}".format(
                                 e.display_image))
                        for e in images.extrafields_set.all()
                    ]
                    response = {
                        "PM10":
                            dict(
                                value=math.ceil(pm_10),
                                color=color_return_pm10(pm_10),
                                quality=quality_return_pm10(
                                    pm_10)),
                        "PM25": dict(
                            value=math.ceil(pm_25),
                            color=color_return_pm25(
                                pm_25),
                            quality=quality_return_pm25(
                                pm_25)),
                        "health_precaution": health_precaution,
                        "area_list": [dict(name=l.name,
                                           id=l.tower_name.id,
                                           tower_id=l.id
                                           ) for l in location]
                    }

                    AirPollutionCurrent.objects.create(
                        pollution_date=datetime.datetime.now().date(),
                        tower=tower, pm10=pm_10,
                        pm25=pm_25)
            return JsonResponse(dict(status=200,
                                     message="success",
                                     payload=response
                                     ))
        else:
            return JsonResponse(dict(
                status=400, message="Key missing", payload={}))


class AirPollutionWeekGeneric(generics.CreateAPIView):
    queryset = AirPollution.objects.all()
    serializer_class = AirPollutionSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            try:
                if request.data:
                    location = request.data.get('location',"")
                else:
                    location = request.POST.get('location', "")
            except Exception:
                return JsonResponse(dict(
                    status=400,
                    message="Location Missing", payload={}))
            # event = Towers.objects.all()
            # nearest = distance(event, [lat, lon])
            # response = air_pollution_weekly(nearest.stationsSelect,
            #                                 nearest.locationsSelect)
            response = air_pollution_weekly_static(location)

            return JsonResponse(dict(status=200,
                                     message="success",
                                     payload=response))
        else:
            return JsonResponse(dict(
                status=400, message="Key missing", payload={}))


class RegistrationGeneric(generics.CreateAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            try:
                if request.data:
                    name = request.data['name']
                    email = request.data['email']
                    phone = request.data['phone']
                    device_id = request.data['device_id']
                else:
                    name = request.POST.get('name', "")
                    email = request.POST.get('email', "")
                    phone = request.POST.get('phone', "")
                    device_id = request.POST.get('device_id', "")
            except Exception:
                return JsonResponse(dict(
                    status=400, message="All key are mandatory", payload={}))
            try:
                device = Registration.objects.get(email=email)
                return JsonResponse(dict(
                    status=200, message="Already registered", payload={}))
            except Exception:
                device = Registration.objects.create(
                    email=email, name=name, phone=phone, device_id=device_id)
                html_content = render_to_string("thankyou.html")
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives('UnitedforAir', text_content,
                                             "UnitedforAir <no-reply@unitedforair.in>",
                                             [email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                return JsonResponse(dict(
                    status=200, message="User Registered", payload={}))
        else:
            return JsonResponse(dict(
                status=400, message="Key missing", payload={}))


class BlogCategoryWebListGeneric(generics.CreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            try:
                if request.data:
                    category_id = request.data['category_id']
                else:
                    category_id = request.POST.get('category_id', "")
                blog_category = BlogCategories.objects.get(id=int(category_id))

            except Exception:
                return JsonResponse(dict(
                    status=400,
                    message="Blog Category ID Missing",
                    payload={}))
            blog = Blog.objects.filter(
                category=blog_category).order_by("-created_date")[:50]
            response = []
            for e in blog:
                response.append(
                    dict(
                        category=e.category.name,
                        category_id=e.category.id,
                        id=e.id,
                        heading=e.heading,
                        description=e.description,
                        event_image="https://api.unitedforair.in/media/{}".format(e.blog_image),
                        create_date=e.created_date,
                    )
                )
            return JsonResponse(dict(status=200,
                                     message="success",
                                     payload={"blog": response}))
        else:
            return JsonResponse(dict(
                status=400, message="Key missing", payload={}))


class UserSubscribeGeneric(generics.CreateAPIView):
    queryset = UserSubscribe.objects.all()
    serializer_class = UserSubscribeSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            try:
                if request.data:
                    email = request.data['email']
                else:
                    email = request.POST.get('email', "")
            except Exception:
                return JsonResponse(dict(
                    status=400,
                    message="Email Missing",
                    payload={}))
            validated = is_valid_email(email)
            if validated:
                try:
                    blog_category = UserSubscribe.objects.get(email=email)
                    message = "Already Subscribed"
                    status = 200
                except Exception:
                    blog_category = UserSubscribe.objects.create(email=email)

                    html_content = render_to_string("thankyou.html")
                    text_content = strip_tags(html_content)
                    msg = EmailMultiAlternatives('UnitedforAir', text_content,
                                                 settings.EMAIL_HOST_USER,
                                                 [email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    message = "Subscribed"
                    status = 200
            else:
                message = "Please enter correct Email"
                status = 200
            return JsonResponse(dict(status=status,
                                     message=message,
                                     payload={}))
        else:
            return JsonResponse(dict(
                status=400, message="Key missing", payload={}))


class EventWebGeneric(generics.CreateAPIView):
    """
    Class for fetching all the upcoming and past events
    """
    queryset = Events.objects.all()
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) == \
                settings.API_VERSION:

            today = datetime.datetime.now().date()
            events_future = Events.objects.filter(event_date__gte=today).\
                order_by("event_date")
            events_past = Events.objects.filter(event_date__lt=today).\
                order_by("-event_date")
            future_events = event_data_web(events_future)
            past_events = event_data_web(events_past)
            return JsonResponse(dict(status=200,
                                message="success",
                                payload=dict(
                                    upcoming_event=future_events,
                                    past_events=past_events,
                                    past_event_count=events_past.count(),
                                    upcoming_event_count=events_future.count(),
                                )
                                ))
        else:
            return JsonResponse(dict(status=400, message="Key missing",
                                     payload={}))


class NotificationGeneric(generics.CreateAPIView):
    """
    Class for fetching all the upcoming and past events
    """
    queryset = UserNotification.objects.all()
    serializer_class = UserNotificationSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) == \
                settings.API_VERSION:
            try:
                if request.data:
                    device_id = request.data['device_id']
                    location_id = request.data['location_id']
                    # lon = request.data['lon']
                    device_type = request.data['device_type']
                else:
                    device_id = request.POST.get('device_id', "")
                    location_id = request.POST.get('location_id', "")
                    # lon = request.POST.get('lon', "")
                    device_type = request.POST.get('device_type', "")
            except Exception:
                return JsonResponse(dict(
                    status=400, message="All key are mandatory", payload={}))
            push_service = FCMNotification(api_key=settings.FIRE_BASE_API_KEY)
            location = Location.objects.get(id=location_id)
            # events = Events.objects.filter(latitude__lte=lat, longitude__lte=lon)
            date = datetime.datetime.now().date()
            events = Events.objects.filter(location=location, event_date=date)
            for e in events:
                try:
                    user_dev = UserNotification.objects.get(
                        device_token=device_id, event=e, device_type=device_type)
                    print user_dev
                except Exception:
                    user_dev = UserNotification.objects.create(
                        device_token=device_id, event=e, device_type=device_type)

                    push_service.notify_single_device(
                        registration_id=device_id,
                        message_title=e.heading, message_body=e.description)

            status = 200
            message = "Notification sent"
            return JsonResponse(dict(
                status=status, message=message, payload={}))


# class ApplicationVersionGeneric(generics.CreateAPIView):
#     """
#     Class for fetching all the upcoming and past events
#     """
#     queryset = ApplicationVersion.objects.all()
#     serializer_class = VersionSerializer
#
#     def create(self, request, *args, **kwargs):
#         if request.method == "POST" and \
#                 request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
#                 and request.META.get('HTTP_X_API_VERSION', None) == \
#                 settings.API_VERSION:
#             if request.data:
#                 android_version = request.data['android_version']
#             else:
#                 android_version = request.POST.get('android_version', "")
#             if not android_version:
#                 message = "Key Missing"
#                 status = 400
#             else:
#                 version = ApplicationVersion.objects.latest('id')
#                 if android_version < version.android_version:
#                     message = "please update"
#                     status = 200
#                 else:
#                     # version.android_version = android_version
#                     # version.save()
#                     message = "success"
#                     status = 200
#
#
#             return JsonResponse(dict(
#                 status=status, message=message, payload={}))


class ApplicationVersionGetGeneric(generics.CreateAPIView):
    """
    Class for fetching all the upcoming and past events
    """
    queryset = ApplicationVersion.objects.all()
    serializer_class = VersionSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) == \
                settings.API_VERSION:
            version = ApplicationVersion.objects.latest('id')
            message = "success"
            status = 200
            payload = dict(version=version.android_version)
            return JsonResponse(dict(
                status=status, message=message, payload=payload))


class LocationGeneric(generics.CreateAPIView):
    """
        Class for fetching all the upcoming and past events
        """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) == \
                settings.API_VERSION:
            location = Location.objects.all()
            response = []
            for l in location:
                response.append(
                    dict(location_name=l.name,
                         location_id=l.id,
                         tower_id=l.tower_name.id
                    )
                )
            return JsonResponse(dict(
                status=200, message="succeess", payload=response))
        else:
            return JsonResponse(dict(
                status=400, message="Key Missing", payload=""))


def fetch_date(data):
    data = data['data']
    try:
        pm10 = [float(x[0]) for x in data.values()]
        pm25 = [float(x[1]) for x in data.values()]
    except Exception:
        pm10 = [float(x[0]) for x in data]
        pm25 = [float(x[1]) for x in data]
    if len(pm10) > 0 and len(pm25) > 0:
        return pm10[-1], pm25[-1]
    else:
        pm10 = random.randrange(250, 450)
        pm25 = random.randrange(250, 350)
        return pm10, pm25


def fetch_data_api(hour, location):
    formDate = (
            datetime.datetime.now() -
            datetime.timedelta(hours=hour)
    ).strftime("%d-%m-%Y %H:%M:%S")
    url = "http://www.envirotechlive.com/app/Actions/DataPullAPIAction.php"

    querystring = {"call": "GetStationData",
                   "fromDate": formDate,
                   "folderSeq": location}
    headers = {
        'authorization': "Basic ZW52aXJvdGVjaF9hcW1zcDpTeXN0ZW0jOTA4MTA=",
        'content-type': "application/json",
    }

    response = requests.request("POST", url, headers=headers,
                                params=querystring)
    print response.json()
    return response


class AirPollutionNew(generics.CreateAPIView):
    queryset = AirPollution.objects.all()
    serializer_class = AirPollutionSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) == \
                settings.API_VERSION:
            try:
                if request.data:
                    location = request.data.get('location', "")
                else:
                    location = request.POST.get('location', "")
            except Exception:
                return JsonResponse(dict(
                    status=400,
                    message="Location Missing", payload={}))
            if location == "1":
                location = 283
            else:
                location = 284
            hour = 2
            response = fetch_data_api(hour, location)
            if len(response.json()['data']) == 0:
                hour = 3
                response = fetch_data_api(hour, location)
            else:
                hour = 4
                response = fetch_data_api(hour, location)
            pm10_data, pm25_data = fetch_date(response.json())

            pm10 = round(float(pm10_data), 2)
            pm25 = round(float(pm25_data), 2)

            images = AirQuality.objects.get(name__startswith=quality_return_pm10(
                pm10).capitalize(), pm_type="PM10")
            health_precaution = [
                dict(preference_text=e.display_text,
                     preference_image="https://api.unitedforair.in/static/"
                                      "images/tips/{}".format(e.display_image))
                for e in images.extrafields_set.all()
            ]
            tower = Towers.objects.get(stationsSelect=location)
            locations = Location.objects.all().order_by('name')
            try:
                poll = AirPollutionCurrent.objects.get(
                    pollution_date=datetime.datetime.now().date(),
                    tower=tower)
                if pm10 != poll.pm10 or pm25 != poll.pm25:
                    poll.pm10 = pm10
                    poll.pm25 = pm25
                    response = {
                        "PM10":
                            dict(
                                value=poll.pm10,
                                color=color_return_pm10(
                                    poll.pm10),
                                quality=quality_return_pm10(poll.pm10)),
                        "PM25": dict(
                            value=poll.pm25,
                            color=color_return_pm25(
                                poll.pm25),
                            quality=quality_return_pm25(
                                poll.pm25)),
                        "health_precaution": health_precaution,
                        "area_list": [dict(name=l.name,
                                           id=l.tower_name.id,
                                           tower_id=l.id
                                           ) for l in locations]
                    }
                else:
                    response = {
                        "PM10":
                            dict(
                                value=pm10,
                                color=color_return_pm10(
                                    pm10),
                                quality=quality_return_pm10(
                                    pm10)),
                        "PM25": dict(
                            value=pm25,
                            color=color_return_pm25(
                                pm25),
                            quality=quality_return_pm25(
                                pm25)),
                        "health_precaution": health_precaution,
                        "area_list": [dict(name=l.name,
                                           id=l.tower_name.id,
                                           tower_id=l.id
                                           ) for l in locations]
                    }
            except Exception:
                response = {
                    "PM10":
                        dict(
                            value=pm10,
                            color=color_return_pm10(
                                pm10),
                            quality=quality_return_pm10(
                                pm10)),
                    "PM25": dict(
                        value=pm25,
                        color=color_return_pm25(
                            pm25),
                        quality=quality_return_pm25(
                            pm25)),
                    "health_precaution": health_precaution,
                    "area_list": [dict(name=l.name,
                                       id=l.tower_name.id,
                                       tower_id=l.id
                                       ) for l in locations]
                }
                AirPollutionCurrent.objects.create(
                    pollution_date=datetime.datetime.now().date(),
                    tower=tower, pm10=pm10, pm25=pm25)
            return JsonResponse(dict(status=200,
                                     message="success",
                                     payload=response
                                     ))


class AirPollutionWeekNewGeneric(generics.CreateAPIView):
    queryset = AirPollution.objects.all()
    serializer_class = AirPollutionSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST" and \
                request.META.get("HTTP_X_API_KEY") == settings.HTTP_API_KEY \
                and request.META.get('HTTP_X_API_VERSION', None) ==\
                settings.API_VERSION:
            try:
                if request.data:
                    location = request.data.get('location',"")
                else:
                    location = request.POST.get('location', "")
            except Exception:
                return JsonResponse(dict(
                    status=400,
                    message="Location Missing", payload={}))
            if location == "1":
                location = 283
            else:
                location = 284
            pm10_list, pm25_list = [], []
            for i in range(5):
                url = "http://www.envirotechlive.com/app/Actions/DataPullAPIAction.php"
                formDate = (datetime.datetime.now() -
                            datetime.timedelta(hours=1))
                last_date = (formDate - datetime.timedelta(days=i))
                querystring = {
                    "call": "GetStationData",
                    "fromDate": last_date.strftime("%d-%m-%Y %H:%M:%S"),
                    "folderSeq": location
                }
                headers = {
                    'authorization': "Basic ZW52aXJvdGVjaF9hcW1zcDpTeXN0ZW0jOTA4MTA=",
                    'content-type': "application/json",
                }

                response = requests.request("POST", url, headers=headers,
                                            params=querystring)
                pm10, pm25 = fetch_date(response.json())
                pm10 = int(pm10)
                pm25 = int(pm25)
                pm10_list.append(dict(
                    date=last_date.strftime("%d-%m-%Y"),
                    maximum=pm10,
                    minimum=pm10,
                    color_max=color_return_pm10(pm10),
                    color_min=color_return_pm10(pm10),
                ))
                pm25_list.append(dict(
                    date=last_date.strftime("%d-%m-%Y"),
                    maximum=pm25,
                    minimum=pm25,
                    color_max=color_return_pm25(pm25),
                    color_min=color_return_pm25(pm25)

                ))
                tower = Towers.objects.get(stationsSelect=location)

                AirPollutionWeekly.objects.create(
                    pollution_date=last_date.date(),
                    pm10_max=pm10,
                    pm10_min=pm10,
                    pm25_max=pm25,
                    pm25_min=pm25,
                    tower=tower
                )
            return JsonResponse(dict(status=200,
                                     message="success",
                                     payload=dict(pm25=pm25_list,
                                                  pm10=pm10_list,
                                                  pm_scale=pollutant_list())))
        else:
            return JsonResponse(dict(
                status=400, message="Key missing", payload={}))


def mailer(request):

    return HttpResponse("Success")


def privacy_policy(request):
    return render(request, "privacy.html")


def terms_and_condition(request):
    return render(request, "privacy.html")


def about_us(request):
    return render(request, "about_us.html")


def jigsaw(request):
    return render(request, "jig.html")