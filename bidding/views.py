try:
    from urllib.parse import quote_plus
except:
    pass
import datetime
import hashlib
from django.utils import timezone
from decimal import Decimal
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
from django.db.models import Q
# Create your views here.
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from .models import Seller, AuctionEvent, Item, ItemCategory, Sales
from .forms import SellerProfileForm, ItemForm, AuctionEventForm, BidForm, PaymentForm, SalesForm, EditProfileForm

from .constants import (AUCTION_EVENT_SHIPPING_CHOICES,
                        AUCTION_EVENT_SHIPPING_USPS,
                        AUCTION_ITEM_CONDITION_CHOICES,
                        AUCTION_ITEM_STATUS_CHOICES,
                        AUCTION_ITEM_STATUS_IDLE,
                        SALES_PAYMENT_STATUS_CHOICES,
                        AUCTION_ITEM_STATUS_RUNNING,
                        SALES_PAYMENT_STATUS_PROCESSING,
                        AUCTION_ITEM_STATUS_SOLD,
                        AUCTION_EVENT_SORTING_CHOICES,
                        AUCTION_EVENT_SORTING_TITLE
                        )
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']
from .utils import process_ended_auction

def index(request):
    if request.user.is_authenticated():
        request.session['message'] = ''
        return HttpResponseRedirect(reverse('user_home'))
    else:
        return HttpResponseRedirect(reverse('view_auction_events'))


@login_required
def view_user_home(request):
    current_auctions = AuctionEvent.objects.filter(item__seller=request.user, item__status=AUCTION_ITEM_STATUS_RUNNING)
    won_auctions = AuctionEvent.objects.filter(winning_bidder=request.user, item__status=AUCTION_ITEM_STATUS_SOLD)
    listable_items = Item.objects.filter(seller=request.user, status=AUCTION_ITEM_STATUS_IDLE)
    has_seller = False
    try:
        seller_profile = Seller.objects.get(user=request.user)
        has_seller = True
    except Seller.DoesNotExist:
        pass
    context = {
        'current_auctions': current_auctions,
        'won_auctions': won_auctions,
        'listable_items': listable_items,
        'has_seller': has_seller
              }
    return render(request, 'bidapp/view_user_home.html', context)


@login_required
def list_item(request):
    try:
        seller_profile = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return messages.error(request, 'You have to create a seller profile first.')
        #HttpResponseRedirect('/')

    if request.method == 'POST':
        item_form = ItemForm(data=request.POST, files=request.FILES, seller=request.user)
        auction_form = AuctionEventForm(data=request.POST)

        if item_form.is_valid() and auction_form.is_valid():
            item = item_form.save(commit=False)
            item.image = request.FILES['image']
            file_type = item.image.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                messages.error(request, 'Invalid image format.')
                return render(request, 'bidapp/bidapp_list.html', {'item_form': item_form, 'auction_form': auction_form})
            auction_event = auction_form.save(item=item)
            return HttpResponseRedirect(reverse('view_auction_event', args=[auction_event.id]))
    else:
        item_form = ItemForm()
        auction_form = AuctionEventForm(initial={'shipping_method': seller_profile.default_shipping_method, 'shipping_detail': seller_profile.default_shipping_detail, 'payment_detail': seller_profile.default_payment_detail})

    context = {
        'item_form': item_form,
        'auction_form': auction_form
              }
    return render(request, 'bidapp/bidapp_list.html', context)

# ***********************************


def view_auction_events(request):
    try:
        auction_events = AuctionEvent.objects.get_current_auctions().filter(~Q(item__seller=request.user))
    except Exception as e:
        auction_events = AuctionEvent.objects.get_current_auctions()
    if request.user.is_staff or request.user.is_superuser:
        auction_events = AuctionEvent.objects.all()

    query = request.GET.get("q")
    if query:
        auction_events = auction_events.filter(
            Q(item__title__icontains=query) |
            Q(item__category__title__icontains=query)
        )
    auction_paginator = Paginator(auction_events, 4)
    page_request_var = "page"
    page = request.GET.get(page_request_var)

    try:
        auction_page = auction_paginator.page(page)
    except PageNotAnInteger:
        auction_page = auction_paginator.page(1)
    except (EmptyPage, InvalidPage):
        auction_page = auction_paginator.page(auction_paginator.num_pages)

    return render(request, 'bidapp/view_auctions.html', {'auction_page': auction_page, 'page_request_var': page_request_var})


def view_auction_event(request, pk):
    try:
        auction_event = AuctionEvent.objects.get(pk=pk)
    except AuctionEvent.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = BidForm(data=request.POST, auction_event=auction_event, bidder=request.user)
        if form.is_valid():
            bid = form.save()
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = BidForm(initial={'amount': auction_event.get_current_price() + Decimal('0.01')})

    context = {
        'form': form,
        'auction_event': auction_event,
    }
    return render(request, 'bidapp/view_auction.html', context)


@login_required
def view_ended_auction_event(request, pk):
    try:
        auction_event = AuctionEvent.objects.get(pk=pk)
    except AuctionEvent.DoesNotExist:
        raise Http404

    if not auction_event.is_running():
        process_ended_auction(auction_event)

    return render(request, 'bidapp/view_ended_auction.html', {'auction_event': auction_event})

@login_required
def view_bid_history(request, pk):
    try:
        auction_event = AuctionEvent.objects.get(pk=pk)
    except AuctionEvent.DoesNotExist:
        raise Http404

    bids = auction_event.bids.all()
    if bids.count():
        highest_bid = auction_event.bids.order_by('-amount')[0]
    else:
        highest_bid = None

    context = {
        'auction_event': auction_event,
        'highest_bid': highest_bid,
        'bids': bids
              }

    return render(request, 'bidapp/view_bid_history.html', context)

@login_required
def list_existing_item(request, pk):
    try:
        item = Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        raise Http404

    if item.status == AUCTION_ITEM_STATUS_RUNNING:
        auction_event = AuctionEvent.objects.get(item=item)
        return HttpResponseRedirect(reverse('view_auction_event', args=[auction_event.pk]))

    if request.method == 'POST':
        auction_form = AuctionEventForm(data=request.POST)
        if auction_form.is_valid():
            auction_event = auction_form.save(item=item)
            return HttpResponseRedirect(reverse('view_auction_event', args=[auction_event.pk]))
    else:
        auction_form = AuctionEventForm()

    context = {
        'item': item,
        'auction_form': auction_form
              }
    return render(request, 'bidapp/list_existing_item.html', context)


@login_required
def view_item(request, pk):
    try:
        item = Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        raise Http404

    item_locked = False
    if item.status == AUCTION_ITEM_STATUS_RUNNING:
        item_locked = True

    context = {
        'item': item,
        'item_locked': item_locked
            }
    return render(request, 'bidapp/view_item_detail.html', context)


@login_required
def edit_item(request, pk):
    try:
        item = Item.objects.get(pk=pk, seller=request.user)
    except Item.DoesNotExist:
        raise Http404

    if item.status == AUCTION_ITEM_STATUS_RUNNING:
        return HttpResponseRedirect(reverse('view_item_detail', args=[item.pk]))

    if request.method == 'POST':
        item_form = ItemForm(data=request.POST, instance=item)

        if item_form.is_valid():
            saved_item = item_form.save()
            return HttpResponseRedirect(reverse('view_item_detail', args=[saved_item.id]))
    else:
        item_form = ItemForm(instance=item)

    return render(request, 'bidapp/edit_item_detail.html', {'item_form': item_form})

def view_categories(request):
    categories = ItemCategory.objects.all()
    return render(request, 'bidapp/view_categories.html', {'categories': categories})

def view_category(request, pk):
    try:
        category = ItemCategory.objects.get(pk=pk)
    except ItemCategory.DoesNotExist:
        raise Http404

    auction_events = AuctionEvent.objects.get_current_auctions().filter(item__category=category)
    auction_paginator = Paginator(auction_events, 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        auction_page = auction_paginator.page(page)
    except (EmptyPage, InvalidPage):
        auction_page = auction_paginator.page(auction_paginator.num_pages)

    context = {
        'category': category,
        'auction_page': auction_page
              }
    return render(request, 'bidapp/view_category.html', context)


@login_required
def pay_for_item(request, pk):
    try:
        auction_event = AuctionEvent.objects.get(pk=pk)
    except AuctionEvent.DoesNotExist:
        raise Http404

    if auction_event.winning_bidder == request.user:
        if not auction_event.is_paid():
            if request.method == 'POST':
                form = PaymentForm(request.POST)
                if form.is_valid():
                    invoice_hash = hashlib.md5()
                    invoice_hash.update(str(auction_event.pk) + str(auction_event.winning_bidder.pk))

                    sale_record = Sales()
                    sale_record.auction_event = auction_event
                    sale_record.invoice_number = invoice_hash.hexdigest()
                    sale_record.save()
                    return HttpResponseRedirect(reverse('user_home'))
            else:
                form = PaymentForm()

            context = {
                'form': form,
                'auction_event': auction_event
                      }
            return render(request, 'bidapp/pay_for_item.html', context)
        else:
            context = {
                'title': 'Payment Error',
                'summary': "You have already paid for this item.",
                      }
            return render(request, 'error.html', context)
    else:
        context = {
            'title': 'Payment Error',
            'summary': "You are trying to pay for an item you didn't win."
                  }
        return render(request, 'error.html', context)

@login_required
def manage_payments(request):
    sales = Sales.objects.filter(auction_event__item__seller=request.user)
    sales_formset = []
    if request.method == "POST":
        forms_are_valid = True
        for sale in sales:
            sale_form = SalesForm(data=request.POST, instance=sale, prefix=sale.pk)
            if sale_form.is_valid():
                sale_form.save()
                return HttpResponseRedirect(reverse('manage_payments'))
    else:
        for sale in sales:
            sale_form = SalesForm(instance=sale, prefix=sale.pk)
            sales_formset.append({'sale': sale, 'form': sale_form})
    return render(request, "bidapp/manage_payments.html", {'sales_formset': sales_formset})

def sign_in(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            if form.user_cache is not None:
                user = form.user_cache
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('user_home')) # TODO: go to profile
                else:
                    messages.error(
                        request,
                        "That user account has been disabled."
                    )
            else:
                messages.error(
                    request,
                    "Username or password is incorrect."
                )
    return render(request, 'bidapp/sign_in.html', {'form': form})


def sign_up(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            login(request, user)
            messages.success(
                request,
                "You're now a user! You've been signed in, too."
            )
            return HttpResponseRedirect(reverse('user_home'))  # TODO: go to profile
    return render(request, 'bidapp/sign_up.html', {'form': form})


def sign_out(request):
    logout(request)
    messages.success(request, "You've been signed out. Come back soon!")
    return HttpResponseRedirect(reverse('view_auction_events'))


def create_item(request):
    form = ItemForm()
    if request.method == 'POST':
        form = ItemForm(data=request.POST, files=request.FILES, seller=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            item.image = request.FILES['image']
            file_type = item.image.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                messages.error(request, 'Invalid image format.')
                return render(request, 'bidapp/create_item.html', {'form': form})
            item.save()
            messages.success(request, 'Item created successfully')
            return HttpResponseRedirect(reverse('user_home'))

    return render(request, 'bidapp/create_item.html', {'form': form})


#def create_auction(request):
#    form = AuctionEventForm()
#    if request.method == 'POST':
#        form = AuctionEventForm(request.POST)
def seller_profile(request):
    form = SellerProfileForm()
    if request.method == 'POST':
        form = SellerProfileForm(request.POST)
        if form.is_valid():
            try:
                seller = form.save(request.user)
                messages.success(request, 'Profile created successfully')
                return HttpResponseRedirect(reverse('user_home'))
            except Exception as e:
                messages.error(request, 'Error creating profile')
                return HttpResponseRedirect(reverse('seller_profile'))
    return render(request, 'bidapp/seller_profile.html', {'form': form})


def edit_profile(request):
    seller = request.user.seller
    form = EditProfileForm(instance=seller)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=seller)
        if form.is_valid():
            try:
                form.save(request.user)
                messages.success(request, 'Profile edited successfully')
                return HttpResponseRedirect(reverse('user_home'))
            except Exception as e:
                messages.error(request, 'Error editing profile')
                return HttpResponseRedirect(reverse('edit_profile'))
    return render(request, 'bidapp/edit_profile.html', {'form': form, 'seller': seller})