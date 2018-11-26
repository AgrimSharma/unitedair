"""carrierutc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from rest_framework.documentation import include_docs_urls
from .views import *

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include_docs_urls(title='Carrier UTC API', public=False)),
    url(r'^events', EventGeneric.as_view()),
    url(r'^search_event', EventSearchGeneric.as_view()),
    url(r'^event_detail', EventDetailGeneric.as_view()),
    url(r'^interested_event', AddEventInterestedGeneric.as_view()),
    url(r'^blog_categories', BlogCategoryGeneric.as_view()),
    url(r'^blog_list', BlogCategoryListGeneric.as_view()),
    url(r'^blog_detail', BlogDetailGeneric.as_view()),
    url(r'^blog_search', BlogSearchGeneric.as_view()),
    url(r'^air_quality', AirQualityGeneric.as_view()),
    url(r'^air_pollution', AirPollutionGeneric.as_view()),
    url(r'^week_air_pollution', AirPollutionWeekGeneric.as_view()),
    url(r'^registration', RegistrationGeneric.as_view()),
    url(r'^privacy-policy', privacy_policy),
    url(r'^api_blog_web', BlogCategoryWebListGeneric.as_view()),
]
