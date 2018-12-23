from datetime import datetime
from django.utils import timezone
import pytz
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
# from django.contrib.auth import get_user_model
from .constants import (AUCTION_EVENT_SHIPPING_CHOICES,
                        AUCTION_EVENT_SHIPPING_USPS,
                        AUCTION_ITEM_CONDITION_CHOICES,
                        AUCTION_ITEM_STATUS_CHOICES,
                        AUCTION_ITEM_STATUS_IDLE,
                        SALES_PAYMENT_STATUS_CHOICES,
                        AUCTION_ITEM_STATUS_RUNNING,
                        SALES_PAYMENT_STATUS_PROCESSING,

                        )
from django.contrib.auth import settings


class ItemCategory(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __str__(self):
        return self.title


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='seller')
    paypal_email = models.EmailField()
    default_shipping_method = models.IntegerField(choices=AUCTION_EVENT_SHIPPING_CHOICES, default=AUCTION_EVENT_SHIPPING_USPS)
    default_shipping_detail = models.CharField(max_length=100, blank=True, null=True)
    default_payment_detail = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return "Seller profile of %s" % self.user


class Item(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    condition = models.IntegerField(choices=AUCTION_ITEM_CONDITION_CHOICES)
    seller = models.ForeignKey(User, related_name='auction_seller')
    category = models.ForeignKey(ItemCategory, related_name='auction_items')
    status = models.IntegerField(choices=AUCTION_ITEM_STATUS_CHOICES, default=AUCTION_ITEM_STATUS_IDLE)
    image = models.ImageField(upload_to='item/', default=settings.MEDIA_ROOT+'default/'+'fairy-tail.jpg')

    def __str__(self):
        return self.title

    def get_condition(self):
        return dict(AUCTION_ITEM_CONDITION_CHOICES).get(self.condition, 'N/A')

    def get_status(self):
        return dict(AUCTION_ITEM_STATUS_CHOICES).get(self.status, 'N/A')

    class Meta:
        ordering = ['-id']


class AuctionEventManager(models.Manager):
    def get_current_auctions(self):

        current_time = timezone.now()
        return self.filter(item__status=AUCTION_ITEM_STATUS_RUNNING, start_time__lt=current_time, end_time__gt=current_time)



class AuctionEvent(models.Model):
    item = models.ForeignKey(Item, related_name='auction_events')
    shipping_method = models.IntegerField(choices=AUCTION_EVENT_SHIPPING_CHOICES)
    shipping_detail = models.CharField(max_length=100, blank=True)
    payment_detail = models.CharField(max_length=200, blank=True)
    start_time = models.DateTimeField(help_text=u'Format (Hour & Minute are optional): 10/25/2006 14:30')
    end_time = models.DateTimeField(help_text=u'Format (Hour & Minute are optional): 10/25/2006 14:30')
    starting_price = models.DecimalField(default=Decimal('0.00'), max_digits=5, decimal_places=2)
    shipping_fee = models.DecimalField(default=Decimal('0.00'), max_digits=5, decimal_places=2)
    reserve_price = models.DecimalField(default=Decimal('0.00'), blank=True, max_digits=5, decimal_places=2)
    winning_bidder = models.ForeignKey(User, related_name='won_auctions', blank=True, null=True)

    objects = AuctionEventManager()

    def __str__(self):
        return "%s listed on %s" % (self.item.title, self.start_time)

    def has_started(self):

        return timezone.now() >= self.start_time

    def has_ended(self):

        return timezone.now() >= self.end_time

    def is_running(self):
        return self.has_started() and not self.has_ended() and self.item.status == AUCTION_ITEM_STATUS_RUNNING

    def get_shipping_method(self):
        return dict(AUCTION_EVENT_SHIPPING_CHOICES).get(int(self.shipping_method), 'N/A')

    def get_current_price(self):
        current_price = self.starting_price
        bid_count = self.bids.count()
        if bid_count:
            highest_bid = self.bids.order_by('-amount')[0]
            current_price = highest_bid.amount
        return current_price

    def get_time_until_end(self):
        delta = self.end_time - datetime.timezone.now()
        if delta.days < 0:
            return '0 seconds'
        else:
            weeks = delta.days / 7
            days = delta.days % 7
            hours = delta.seconds / 3600
            minutes = (delta.seconds % 3600) / 60
            seconds = (delta.seconds % 3600) % 60

            time_string = ''
            if weeks:
                time_string += '%s weeks ' % weeks
            if days:
                time_string += '%s days ' % days
            if hours:
                time_string += '%s hours ' % hours
            if minutes:
                time_string += '%s minutes ' % minutes
            if seconds:
                time_string += '%s seconds' % seconds

            return time_string

    def is_paid(self):
        return self.sales.count() > 0

    def get_payment_status(self):
        if self.is_paid():
            return dict(SALES_PAYMENT_STATUS_CHOICES).get(self.sales.order_by('payment_status'))
        else:
            return 'Unpaid'

    class Meta:
        ordering = ['-id']

class Sales(models.Model):
    auction_event = models.ForeignKey(AuctionEvent, related_name='sales')
    payment_status = models.IntegerField(choices=SALES_PAYMENT_STATUS_CHOICES, default=SALES_PAYMENT_STATUS_PROCESSING)
    invoice_number = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return "Invoice for %s" % self.auction_event

class Bid(models.Model):
    auction_event = models.ForeignKey(AuctionEvent, related_name='bids')
    bidder = models.ForeignKey(User, related_name='bids')
    amount = models.DecimalField(default=Decimal('0.00'), max_digits=5, decimal_places=2, help_text='All bids are final. Price in US dollars.')

    def __str__(self):
        return "Placed on %s by %s" % (self.auction_event.item.title, self.bidder.username)
