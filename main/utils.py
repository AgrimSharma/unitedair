import math
import requests
import datetime
from .models import *


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
    min_dist = 99999
    resp = ()
    latitude = points[0]
    longitude = points[1]
    for i in range(len(data)):
        vals = data[i]
        dist = (vals.latitude - float(latitude)) ** 2 + (vals.longitude - float(longitude)) ** 2
        eucd = math.sqrt(dist)
        if eucd < min_dist:
            min_dist = eucd
            resp = vals
    return resp


def pollutant_list():
    levels = ['Severe', 'Very Poor', 'Poor', 'Moderately Polluted',
              'Satisfactory', 'Good']
    response = []
    for l in levels:
        pm10_quality = AirQuality.objects.get(name=l, pm_type='PM10')
        pm25_quality = AirQuality.objects.get(name=l, pm_type='PM25')
        response.append(
            dict(
                pm25_value="{}-{}".format(pm25_quality.minimum, pm25_quality.maximum) if pm25_quality.minimum < 251 else ">{}".format(pm25_quality.minimum),
                pm10_value="{}-{}".format(pm10_quality.minimum, pm10_quality.maximum) if pm10_quality.minimum < 431 else ">{}".format(pm10_quality.minimum),
                color_code = pm10_quality.color_code,
                name=pm10_quality.name
            )
        )
    return response


def air_pollution_weekly(locations_select, stations_select):
    pm10_list = []
    pm25_list = []
    current = datetime.datetime.now().date()
    last_week = current - datetime.timedelta(days=5)

    url = "http://www.envirotechlive.com/app/ajax_cpcb.php"
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

        response = requests.request("GET", url, params=querystring)
        data = response.json()

        if len(data['data']) > 0:
            average = data['avgminmax']
            pm10_list.append(dict(
                date=date_str,
                maximum=average['max'][0],
                minimum=average['min'][0]
            ))
            pm25_list.append(dict(
                date=date_str,
                maximum=average['max'][1],
                minimum=average['min'][1]
            ))

    return dict(pm25=pm25_list,
                pm10=pm10_list,
                pm_scale=pollutant_list())


def air_quality_data(locations_select, stations_select):
    current = datetime.datetime.now().date().strftime("%d-%m-%Y")
    current_ct = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    url = "http://www.envirotechlive.com/app/ajax_cpcb.php"

    querystring = {"method": "requestStationReport",
                   "quickReportType": "today",
                   "isMultiStation": "1", "stationType": "aqmsp",
                   "lastDataDate": "28-11-2018 03:45:00",
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

    response = requests.request("GET", url=url, params=querystring)
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
                event_date=e.event_date,
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
        response.append(
            dict(
                id=e.id,
                heading=e.heading,
                description=e.description,
                event_image=e.event_image,
                event_date=e.event_date,
                event_time=e.event_time,
                event_address=e.event_address,
                latitude=e.latitude,
                longitude=e.longitude
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
                event_image=e.blog_image,
                create_date=e.created_date,
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
        return 'GOOD'.lower()
    elif 31.0 <= val <= 60.0:
        return 'SATISFACTORY'.lower()
    elif 61.0 <= val <= 90.0:
        return 'MODERATE'.lower()
    elif 91.0 <= val <= 120.0:
        return 'POOR'.lower()
    elif 121.0 <= val <= 250.0:
        return 'VERY POOR'.lower()
    else:
        return 'SEVERELY POLLUTED'.lower()


def quality_return_pm10(val):
    """
    :param val: float value of pollution
    :return: return degree of pollution
    """
    val = float(val)
    if 0.0 <= val < 50.0:
        return 'GOOD'.lower()
    elif 51.0 <= val <= 100.0:
        return 'SATISFACTORY'.lower()
    elif 101.0 <= val <= 250.0:
        return 'MODERATE'.lower()
    elif 251.0 <= val <= 350.0:
        return 'POOR'.lower()
    elif 351.0 <= val <= 430.0:
        return 'VERY POOR'.lower()
    else:
        return 'SEVERELY POLLUTED'.lower()


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