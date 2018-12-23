from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'$', index, name='index'),
    url(r'home/$', view_user_home, name='user_home'),
    url(r'item/sell/$', list_item, name='list_item'),
    url(r'item/(?P<pk>\d+)/view/$', view_item, name='view_item_detail'),
    url(r'item/(?P<pk>\d+)/edit/$', edit_item, name='edit_item_detail'),

    url(r'item/buy/$', view_auction_events, name='view_auction_events'),
    url(r'item/auction/(?P<pk>\d+)/$', view_auction_event, name='view_auction_event'),
    url(r'item/auction/(?P<pk>\d+)/bids/$', view_bid_history, name='view_bid_history'),
    url(r'item/(?P<pk>\d+)/sell/$', list_existing_item, name='list_existing_item'),

    url(r'item/auction/(?P<pk>\d+)/ended/$', view_ended_auction_event, name='view_ended_auction_event'),


    url(r'categories/$', view_categories, name='view_categories'),
    url(r'categories/(?P<pk>\d+)/$', view_category, name='view_category'),

    url(r'item/auction/payments/(?P<pk>\d+)/pay/$', pay_for_item, name='pay_for_item'),
    url(r'item/auction/payments/manage/$', manage_payments, name='manage_payments'),

]
