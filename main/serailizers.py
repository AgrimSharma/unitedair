from rest_framework import serializers
from .models import *
import string, random
import re
from django.utils.translation import ugettext_lazy as _


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events


class EventSearchSerializer(serializers.ModelSerializer):
    search_text = serializers.CharField(required=False, help_text=_("Event Heading"))
    search_type = serializers.CharField(required=True, help_text=_("Event Heading"))
    page_no = serializers.IntegerField(required=True)

    class Meta:
        model = Events
        fields = ['search_text', 'search_type', "page_no"]


class EventDetailSerializer(serializers.ModelSerializer):
    event_id = serializers.CharField(required=True, help_text=_("Event ID(Integer)"))
    device_id = serializers.CharField(required=True, help_text=_("Device_id(Integer)"))

    class Meta:
        model = Events
        fields = ['event_id', "device_id"]


class AddEventInterestedSerializer(serializers.ModelSerializer):
    event_id = serializers.CharField(required=True, help_text=_("Event ID"))
    device_id = serializers.CharField(required=True, help_text=_("Device ID"))

    class Meta:
        model = Events
        fields = ['event_id', "device_id"]


class BlogCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = BlogCategories


class BlogSerializer(serializers.ModelSerializer):
    category_id = serializers.CharField(required=True, help_text=_("Blog Category ID"))
    page_no = serializers.CharField(required=True, help_text=_("Page no"))

    class Meta:
        model = Blog
        fields = ["category_id", "page_no"]


class BlogDetailsSerializer(serializers.ModelSerializer):
    blog_id = serializers.CharField(required=True, help_text=_("Blog ID"))

    class Meta:
        model = Blog
        fields = ['blog_id']


class BlogSearchSerializer(serializers.ModelSerializer):
    search_text = serializers.CharField(required=False, help_text=_("Event Heading"))
    search_type = serializers.CharField(required=True, help_text=_("Event Heading"))
    page_no = serializers.IntegerField(required=True)

    class Meta:
        model = Blog
        fields = ['search_text', 'search_type', "page_no"]


class AirQualitySerializer(serializers.ModelSerializer):

    class Meta:
        model = AirQuality


class AirPollutionSerializer(serializers.ModelSerializer):
    lat = serializers.CharField(required=True, help_text=_("Latitude"))
    lon = serializers.CharField(required=True, help_text=_("Longitude"))

    class Meta:
        model = AirPollution
        fields = ['lat', "lon"]


class RegistrationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, help_text=_("Name"))
    email = serializers.EmailField(required=True, help_text=_("email"))
    phone = serializers.CharField(required=True, help_text=_("phone"))
    device_id = serializers.CharField(required=True, help_text=_("Device ID"))

    class Meta:
        model = Registration
        fields = ['name', "email", "phone", "device_id"]


class UserSubscribeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, help_text=_("email"))

    class Meta:
        model = Registration
        fields = ["email"]


class UserNotificationSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(required=True, help_text=_("email"))
    lat = serializers.CharField(required=True, help_text=_("Latitude"))
    lon = serializers.CharField(required=True, help_text=_("Longitude"))

    class Meta:
        model = UserNotification
        fields = ["device_id", "lat", "lon"]