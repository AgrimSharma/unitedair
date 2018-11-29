# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *


class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'event_date'
    list_display = ["heading", "event_date", "event_time"]


class InterestedEventAdmin(admin.ModelAdmin):
    raw_id_fields = ['event']
    list_display = ["event", "device_id", "created_date"]


class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "blog_image", "created_date"]


class AirQualityAdmin(admin.ModelAdmin):
    list_display = ["pm_type", "name", "minimum", "maximum"]


class AirPollutionAdmin(admin.ModelAdmin):
    raw_id_fields = ['towers']
    list_display = ["towers", "pm10", "pm25"]


class TowerAdmin(admin.ModelAdmin):
    list_display = ["location", "latitude", "longitude"]


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "device_id"]


class UserSubscribeAdmin(admin.ModelAdmin):
    list_display = ["email"]


class LocationAdmin(admin.ModelAdmin):
    list_display = ["name"]


class AirPollutionLogsAdmin(admin.ModelAdmin):
    list_display = ["tower_name", "pollution_date", "pm25_max", "pm10_max"]

    def tower_name(self, obj):
        return obj.tower.location


class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ["device", "events", "device_type"]

    def device(self, obj):
        return obj.device_token[:20]

    def events(self, obj):
        return obj.event.heading


class BlogAdmin(admin.ModelAdmin):

    def category_name(self, obj):
        return obj.category.name

    raw_id_fields = ["category"]
    list_display = ["category_name", "heading", "created_date"]


admin.site.register(Events, EventAdmin)
admin.site.register(InterestedEvent, InterestedEventAdmin)
admin.site.register(BlogCategories, BlogCategoryAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(UserSubscribe, UserSubscribeAdmin)
admin.site.register(AirQuality, AirQualityAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(AirPollution, AirPollutionAdmin)
admin.site.register(AirPollutionWeekly, AirPollutionLogsAdmin)
admin.site.register(Towers, TowerAdmin)