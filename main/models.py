# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Events(models.Model):
    heading = models.CharField(max_length=1000)
    description = models.TextField(max_length=2000)
    event_image = models.URLField()
    event_date = models.DateField()
    event_time = models.TimeField()
    event_address = models.CharField(max_length=2000)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_date = models.DateTimeField(auto_now=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-event_date',)
        verbose_name = "Event"
        verbose_name_plural = "Event"

    def __unicode__(self):
        return "{} : {} : {}".format(self.heading, self.event_date, self.event_time)

    def __str__(self):
        return "{} : {} : {}".format(self.heading, self.event_date, self.event_time)


class InterestedEvent(models.Model):
    event = models.ForeignKey(to=Events, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=1000)
    created_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_date',)
        verbose_name = "Interested Event"
        verbose_name_plural = "Interested Event"

    def __unicode__(self):
        return "{} : {}".format(self.event.heading, self.device_id)

    def __str__(self):
        return "{} : {}".format(self.event.heading, self.device_id)


class BlogCategories(models.Model):
    name = models.CharField(max_length=100)
    color_code = models.CharField(max_length=100, null=True, blank=True)
    blog_image = models.URLField()
    created_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_date',)
        verbose_name = "Blog Categories"
        verbose_name_plural = "Blog Categories"

    def __unicode__(self):
        return "{} : {}: {}".format(self.name, self.blog_image, self.created_date)

    def __str__(self):
        return "{} : {}: {}".format(self.name, self.blog_image, self.created_date)


class Blog(models.Model):
    category = models.ForeignKey(to=BlogCategories, on_delete=models.CASCADE)
    heading = models.CharField(max_length=1000)
    description = models.TextField(max_length=2000)
    blog_image = models.URLField()
    created_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_date',)
        verbose_name = "Blog"
        verbose_name_plural = "Blog"

    def __unicode__(self):
        return "{} : {}: {}".format(self.category.name, self.heading, self.created_date)

    def __str__(self):
        return "{} : {}: {}".format(self.category.name, self.heading, self.created_date)


class AirQuality(models.Model):
    name = models.CharField(max_length=100)
    color_code = models.CharField(max_length=100, null=True, blank=True)
    minimum = models.IntegerField()
    maximum = models.IntegerField()
    pm_type = models.CharField(null=True, blank=True, max_length=100)
    display_text = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_date',)
        verbose_name = "Air Quality"
        verbose_name_plural = "Air Quality"

    def __unicode__(self):
        return "{} : {}: {}".format(self.name, self.minimum, self.maximum)

    def __str__(self):
        return "{} : {}: {}".format(self.name, self.minimum, self.maximum)


class Towers(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.CharField(max_length=1000)
    created_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_date',)
        verbose_name = "Towers"
        verbose_name_plural = "Towers"

    def __unicode__(self):
        return "{} : {}: {}".format(self.location, self.latitude, self.longitude)

    def __str__(self):
        return "{} : {}: {}".format(self.location, self.latitude, self.longitude)


class AirPollution(models.Model):
    pm25 = models.FloatField()
    pm10 = models.FloatField()
    towers = models.ForeignKey(to=Towers, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_date',)
        verbose_name = "Air Pollution"
        verbose_name_plural = "Air Pollution"

    def __unicode__(self):
        return "{} : {}: {}".format(self.towers.location, self.pm25, self.pm10)

    def __str__(self):
        return "{} : {}: {}".format(self.towers.location, self.pm25, self.pm10)


class Registration(models.Model):
    name = models.CharField(max_length=1000)
    email = models.EmailField(unique=True)
    device_id = models.CharField(max_length=1000)
    phone = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_date',)
        verbose_name = "Registration"
        verbose_name_plural = "Registration"

    def __unicode__(self):
        return "{}".format(self.email)

    def __str__(self):
        return "{}".format(self.email)


class UserSubscribe(models.Model):
    email = models.EmailField(unique=True)
    created_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_date',)
        verbose_name = "User Subscribe"
        verbose_name_plural = "User Subscribe"

    def __unicode__(self):
        return "{}".format(self.email)

    def __str__(self):
        return "{}".format(self.email)


class UserNotification(models.Model):
    device_token = models.CharField(max_length=2000)
    event = models.ForeignKey(to=Events, on_delete=models.CASCADE)
    device_type = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_date',)
        verbose_name = "User Notification"
        verbose_name_plural = "User Notification"

    def __unicode__(self):
        return "{} : {}".format(self.device_token, self.event.heading)

    def __str__(self):
        return "{} : {}".format(self.device_token, self.event.heading)
