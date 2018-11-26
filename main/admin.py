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
    list_display = ["name", "minimum", "maximum"]


class AirPollutionAdmin(admin.ModelAdmin):
    raw_id_fields = ['towers']
    list_display = ["towers", "pm10", "pm25"]


class TowerAdmin(admin.ModelAdmin):
    list_display = ["location", "latitude", "longitude"]


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "device_id"]


class BlogAdmin(admin.ModelAdmin):

    def category_name(self, obj):
        return obj.category.name

    raw_id_fields = ["category"]
    list_display = ["category_name", "heading", "created_date"]


admin.site.register(Events, EventAdmin)
admin.site.register(InterestedEvent, InterestedEventAdmin)
admin.site.register(BlogCategories, BlogCategoryAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(AirQuality, AirQualityAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(AirPollution, AirPollutionAdmin)
admin.site.register(Towers, TowerAdmin)