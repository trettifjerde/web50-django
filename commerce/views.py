import json
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from commerce.models import Merchant, Listing, Comment, Bid, Category
from commerce.forms import ListingForm, CommentForm
from home.views import login_view, logout_view, register

def commerce_login_view(request):
    return login_view(request, 'commerce/login.html', 'commerce:index')

def commerce_logout_view(request):
    return logout_view(request, 'commerce:index')

def commerce_register(request):
    return register(request, 'commerce/register.html', 'commerce:index')

def index(request):
    listings = Listing.objects.filter(winner=None).order_by('-created')
    return render(request, "commerce/index.html", {"title": "Active listings", "listings": listings})

def categories(request):
    return render(request, 'commerce/categories.html', {'categories': Category.objects.all()})

def category(request, slug):
    try:
        cat = Category.objects.get(slug=slug)
        return render(request, "commerce/index.html", {
            "title": f"{cat.name} listings", 
            "listings": Listing.objects.filter(category=cat, winner=None)
            })
    except:
        pass
    return redirect("commerce:index")

@login_required
def new_listing(request):
    form = ListingForm({"merchant": request.user.merchant, "winner": None, "starting_bid": 0})
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save()
            return redirect('commerce:listing', listing_id=listing.id)
    return render(request, 'commerce/listing_form.html', {"form": form, "action": "new"})

def listing(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
        return render(request, "commerce/listing.html", {"listing": listing, "commentForm": CommentForm()})
    except ObjectDoesNotExist:
        return renderMessagePage(request, {"text": "No such listing", "class": "error"})

@login_required
def edit_listing(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
        if listing.merchant.user == request.user and not listing.winner:
            form = ListingForm(instance=listing)
            if request.method == "POST":
                form = ListingForm(request.POST, request.FILES, instance=listing)
                if form.is_valid():
                    form.save()
                    return redirect("commerce:listing", listing_id=listing_id)
                else:
                    return render(request, "commerce/listing_form.html", {'form': form, 'action': 'edit', 'errors': form.errors})
            return render(request, "commerce/listing_form.html", {'form': form, 'action': 'edit'})
        else:
            raise IntegrityError
    except:
        pass
    return redirect("commerce:listing", listing_id=listing_id)

@login_required
def close_listing(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.load(request)
        try:
            listing = Listing.objects.get(pk=data["listingId"])

            if request.user != listing.merchant.user: 
                raise Exception("not author")
            elif listing.winner:
                raise Exception("listing is already closed")
            elif listing.get_bids_length() == 0:
                raise Exception("no bids to agree to")

            listing.winner = listing.get_current_bid_merchant()
            listing.save()
            return JsonResponse({'redirect': f'{reverse("commerce:listing", args=(listing.id,))}'})
        except Exception as err:
            return JsonResponse({'msg': f'{err}'})
    return redirect("commerce:index")


@login_required
def delete_listing(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.load(request)
            listing = Listing.objects.get(pk=data['listingId'])
            if request.user == listing.merchant.user and not listing.winner:
                listing.delete()
                return JsonResponse({"redirect": reverse("commerce:profile")})
            else:
                raise Exception
        except Exception as err:
            return JsonResponse({"msg": f'{err}'})
    return redirect("commerce:index")

@login_required
def add_comment(request, listing_id):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            try:
                new_comment = form.save(commit=False)
                new_comment.merchant = request.user.merchant
                new_comment.listing = Listing.objects.get(pk=listing_id)
                new_comment.save()
                return redirect("commerce:listing", listing_id=listing_id)
            except: pass

    return renderMessagePage(request, {                    
            "text": "Error while adding a comment", 
            "class": "error",
            "redirect": reverse('listing', args=[listing_id])})

@login_required
def delete_comment(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.load(request)
            comment = Comment.objects.get(pk=data['commentId'])
            if comment.merchant == request.user.merchant:
                comment.delete()
                return JsonResponse({"redirect": ""})
            else:
                raise Exception('not author')
        except Exception as err:
            return JsonResponse({"msg": f'{err}'})
    return redirect("commerce:index")


@login_required
def watchlist_toggle(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.load(request)
            listing = Listing.objects.get(pk=data["listingId"])
            if request.user.is_authenticated and request.user.merchant != listing.merchant:
                merchant = request.user.merchant
                if merchant.watchlist.contains(listing):
                    merchant.watchlist.remove(listing)
                else:
                    merchant.watchlist.add(listing)
                return JsonResponse({"redirect": ""})
            else:
                raise Exception
        except Exception as err:
            return JsonResponse({"msg": f'{err}'})
    return redirect("commerce:index")

@login_required
def bid(request, listing_id):
    if request.method == "POST":
        try:
            listing = Listing.objects.get(pk=listing_id)
            if not listing.winner:
                bid_price = float(request.POST["bid"])
                if bid_price > listing.get_current_bid_price():
                    bid = Bid(price=bid_price, merchant=request.user.merchant, listing=listing)
                    bid.save()
                else:
                    return renderMessagePage(request, {
                        "text": "Your bid is lesser than the current bid", 
                        "class": "error",
                        "redirect": reverse('commerce:listing', args=[listing_id])
                    })
            else:
                return renderMessagePage(request, {
                        "text": "This listing is closed", 
                        "class": "error",
                        "redirect": reverse('commerce:listing', args=[listing_id])
                    })
        except:
            pass
    return redirect("commerce:listing", listing_id=listing_id)

def merchant(request, merchant_id):
    try:
        merchant = Merchant.objects.get(pk=merchant_id)
        return render(request, "commerce/merchant.html", {"merchant": merchant})
    except ObjectDoesNotExist:
        return renderMessagePage(request, {"text": "No such merchant", "class": "error"})

def renderMessagePage(request, context):
    return render(request, "commerce/404.html", context)
        
@login_required
def profile(request):
    return redirect("commerce:merchant", merchant_id=request.user.merchant.id)

@login_required
def watchlist(request):
    return render(request, "commerce/index.html", {"title": "Watchlist", "listings": request.user.merchant.watchlist.all()})

