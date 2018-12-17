# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *


class EventImageAdmin(admin.TabularInline):
    model = EventImage
    extra = 0


class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'event_date'
    list_display = ["heading", "event_date", "event_time"]
    inlines = [EventImageAdmin]


class InterestedEventAdmin(admin.ModelAdmin):
    raw_id_fields = ['event']
    list_display = ["event", "device_id", "created_date"]


class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "blog_image", "created_date"]


class ExtraFieldAdmin(admin.TabularInline):
    model = ExtraFields
    extra = 0


class AirQualityAdmin(admin.ModelAdmin):
    list_display = ["pm_type", "name", "minimum", "maximum"]
    inlines = (ExtraFieldAdmin,)


class AirPollutionAdmin(admin.ModelAdmin):
    raw_id_fields = ['towers']
    list_display = ["tower_name", "pm10", "pm25"]

    def tower_name(self, obj):
        return obj.towers.locations


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "device_id"]


class UserSubscribeAdmin(admin.ModelAdmin):
    list_display = ["email"]


class PinCodeAdmin(admin.ModelAdmin):
    list_display = ["pin_code"]


class LocationAdmin(admin.TabularInline):
    model = Location
    extra = 0


class TowerAdmin(admin.ModelAdmin):
    list_display = ["locations"]
    inlines = (LocationAdmin,)


class VersionAdmin(admin.ModelAdmin):
    list_display = ["android_version"]


class AirPollutionLogsAdmin(admin.ModelAdmin):
    list_display = ["tower_name", "pollution_date", "pm25_max", "pm10_max"]
    
    def tower_name(self, obj):
        return obj.tower.locations


class AirPollutionCurrentAdmin(admin.ModelAdmin):
    list_display = ["tower_name", "pollution_date", "pm25", "pm10"]

    def tower_name(self, obj):
        return obj.tower.locations


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
# admin.site.register(Location, LocationAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(AirPollutionCurrent, AirPollutionCurrentAdmin)
admin.site.register(ApplicationVersion, VersionAdmin)
admin.site.register(AirPollution, AirPollutionAdmin)
admin.site.register(AirPollutionWeekly, AirPollutionLogsAdmin)
admin.site.register(Towers, TowerAdmin)