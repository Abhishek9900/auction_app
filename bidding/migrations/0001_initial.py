# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-30 11:22
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuctionEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shipping_method', models.IntegerField(choices=[(1, 'USPS'), (2, 'FedEx'), (3, 'UPS'), (4, 'DHL')])),
                ('shipping_detail', models.CharField(blank=True, max_length=100)),
                ('payment_detail', models.CharField(blank=True, max_length=200)),
                ('start_time', models.DateTimeField(help_text='Format (Hour & Minute are optional): 10/25/2006 14:30')),
                ('end_time', models.DateTimeField(help_text='Format (Hour & Minute are optional): 10/25/2006 14:30')),
                ('starting_price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('shipping_fee', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('reserve_price', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='All bids are final. Price in US dollars.', max_digits=5)),
                ('auction_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='bidding.AuctionEvent')),
                ('bidder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('condition', models.IntegerField(choices=[(1, 'Used'), (2, 'Used Like New'), (3, 'New')])),
                ('status', models.IntegerField(choices=[(1, 'Idle'), (2, 'Running'), (3, 'On Hold'), (4, 'Sold'), (5, 'Expired'), (6, 'Disputed')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bidding.ItemCategory')),
            ],
        ),
        migrations.CreateModel(
            name='Sales',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_status', models.IntegerField(choices=[(1, 'Processing'), (2, 'Cleared'), (3, 'Disputed'), (4, 'Refunded')], default=1)),
                ('invoice_number', models.CharField(max_length=200, unique=True)),
                ('auction_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='bidding.AuctionEvent')),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paypal_email', models.EmailField(max_length=254)),
                ('default_shipping_method', models.IntegerField(choices=[(1, 'USPS'), (2, 'FedEx'), (3, 'UPS'), (4, 'DHL')], default=1)),
                ('default_shipping_detail', models.CharField(blank=True, max_length=100, null=True)),
                ('default_payment_detail', models.CharField(blank=True, max_length=200, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='seller', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auction_items', to='bidding.ItemCategory'),
        ),
        migrations.AddField(
            model_name='item',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auction_items', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='auctionevent',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auction_events', to='bidding.Item'),
        ),
        migrations.AddField(
            model_name='auctionevent',
            name='winning_bidder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='won_auctions', to=settings.AUTH_USER_MODEL),
        ),
    ]