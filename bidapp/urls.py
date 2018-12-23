"""bidapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from bidding.views import *
from django.conf.urls.static import static
from django.conf import settings
#from bidding.views import (
#    list_item, index,
#    view_user_home,
#    view_auction_events,
#    view_auction_event,
#    view_bid_history,
#    list_existing_item,
#    view_ended_auction_event,
#    view_item,
#    edit_item,
#    view_categories,
#    view_category,
#    pay_for_item,
#    manage_payments
#    )

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index, name='index'),
    url(r'^home/$', view_user_home, name='user_home'),
    url(r'^item/sell/$', list_item, name='list_item'),
    url(r'^item/(?P<pk>\d+)/view/$', view_item, name='view_item_detail'),
    url(r'^item/(?P<pk>\d+)/edit/$', edit_item, name='edit_item_detail'),

    url(r'^item/buy/$', view_auction_events, name='view_auction_events'),
    url(r'^item/auction/(?P<pk>\d+)/$', view_auction_event, name='view_auction_event'),
    url(r'^item/auction/(?P<pk>\d+)/bids/$', view_bid_history, name='view_bid_history'),
    url(r'^item/(?P<pk>\d+)/sell/$', list_existing_item, name='list_existing_item'),

    url(r'^item/auction/(?P<pk>\d+)/ended/$', view_ended_auction_event, name='view_ended_auction_event'),

    url(r'^categories/$', view_categories, name='view_categories'),
    url(r'^categories/(?P<pk>\d+)/$', view_category, name='view_category'),

    url(r'^item/auction/payments/(?P<pk>\d+)/pay/$', pay_for_item, name='pay_for_item'),
    url(r'^item/auction/payments/manage/$', manage_payments, name='manage_payments'),

    url(r'^create_item/$', create_item, name='create_item'),
    url(r'^seller_profile/$', seller_profile, name='seller_profile'),
    url(r'^edit_profile/$', edit_profile, name='edit_profile'),

    url(r'^sign_in/$', sign_in, name='sign_in'),
    url(r'^sign_up/$', sign_up, name='sign_up'),
    url(r'^sign_out/$', sign_out, name='sign_out'),
]

if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)