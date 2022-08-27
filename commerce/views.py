import json
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, reverse, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormView

from commerce.models import Merchant, Listing, Comment, Bid, Category
from commerce.forms import ListingForm, CommentForm

def is_ajax_and_post(function):
    def inner(request):
        if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return function(request)
        else:
            return redirect('commerce:index')
    return inner


class ListingsView(ListView):
    model = Listing
    template_name = 'commerce/index.html'
    queryset = Listing.objects.filter(winner=None)
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Active listings'
        context['categories'] = Category.objects.all()
        return context

class WatchlistView(LoginRequiredMixin, ListingsView):
    def get_queryset(self):
        return self.request.user.merchant.watchlist.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Watchlist'
        context['categories'] = []
        return context

class CategoryView(ListingsView):
    def get_queryset(self):
        cat = get_object_or_404(Category, slug=self.kwargs['slug'])
        return cat.listings.filter(winner=None)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat_name = self.kwargs['slug'].replace('-', ' ')
        context['title'] = f'{cat_name} listings'
        return context

class CategoriesView(ListView):
    model = Category
    template_name = 'commerce/categories.html'

class ListingView(DetailView):
    model = Listing

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['commentForm'] = CommentForm()

        comments = get_object_or_404(Listing, pk=self.kwargs['pk']).comments.all()
        paginator = Paginator(comments, 5)
        page_number = self.request.GET.get('page')
        page = paginator.get_page(page_number)
        context['page'] = page

        return context

class MerchantView(DetailView):
    model = Merchant

class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm

    def form_valid(self, form):
        form.instance.merchant = self.request.user.merchant
        return super().form_valid(form)

class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    form_class = ListingForm

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.merchant.user

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ['post']

    def http_method_not_allowed(self, *args, **kwargs):
        return redirect('commerce:listing', pk=self.kwargs['pk'])

    def form_valid(self, form):
        form.instance.listing = get_object_or_404(Listing, pk=self.kwargs['pk'])
        form.instance.merchant = self.request.user.merchant
        return super().form_valid(form)

    def form_invalid(self, form):
        return redirect('commerce:listing', pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('commerce:listing', kwargs={'pk': self.kwargs['pk']})


@login_required
def profile(request):
    return redirect("commerce:merchant", pk=request.user.merchant.id)

@is_ajax_and_post
@login_required
def close_listing(request):
    data = json.loads(request.body)
    listing = get_object_or_404(Listing, pk=data["pk"])

    if request.user.merchant != listing.merchant: 
        raise Exception("not author")
    elif listing.winner:
        raise Exception("listing is already closed")
    elif listing.bids.count() == 0:
        raise Exception("no bids to agree to")

    listing.winner = listing.current_bid_merchant()
    listing.save()
    return JsonResponse({'redirect': ''})

@is_ajax_and_post
@login_required
def delete_listing(request):
    try:
        data = json.loads(request.body)
        listing = Listing.objects.get(pk=data['pk'])
        if request.user == listing.merchant.user and not listing.winner:
            listing.delete()
            return JsonResponse({"redirect": reverse("commerce:profile")})
        else:
            return JsonResponse({"error": "Listing can't be deleted"})
    except Exception:
        return JsonResponse({"redirect": reverse('commerce:index')})

@is_ajax_and_post
@login_required
def delete_comment(request):
    try:
        data = json.loads(request.body)
        comment = Comment.objects.get(pk=data['pk'])
        if comment.merchant == request.user.merchant:
            comment.delete()
            return JsonResponse({"redirect": ""})
        else:
            raise Exception('not author')
    except Exception as err:
        return JsonResponse({"msg": f'{err}'})

@is_ajax_and_post
@login_required
def watchlist_toggle(request):
    data = json.loads(request.body)
    listing = Listing.objects.get(pk=data["pk"])
    if request.user.merchant != listing.merchant:
        merchant = request.user.merchant
        if merchant.watchlist.contains(listing):
            merchant.watchlist.remove(listing)
        else:
            merchant.watchlist.add(listing)
        return JsonResponse({"redirect": ""})

@is_ajax_and_post
@login_required
def bid(request):
    try:
        data = json.loads(request.body)
        listing = Listing.objects.get(pk=data['pk'])
        if not listing.winner:
            if data['bid']:
                bid_price = int(data['bid'])
                if bid_price > listing.current_bid_price():
                    bid = Bid(price=bid_price, merchant=request.user.merchant, listing=listing)
                    bid.save()
                    return JsonResponse({'redirect': ""})
                else:
                    return JsonResponse({'error': 'Your bid must be higher than the current price'})
            else:
                return JsonResponse({'error': 'Enter a number'})
        return JsonResponse({'redirect': ""})
    except:
        return JsonResponse({'error': 'An error occured. Try again later'})


'''
def index(request):
    listings = Listing.objects.filter(winner=None).order_by('-created')
    return render(request, "commerce/index.html", {"title": "Active listings", "listings": listings})

def categories(request):
    return render(request, 'commerce/categories.html', {'categories': Category.objects.all()})

@login_required
def watchlist(request):
    return render(request, "commerce/index.html", {"title": "Watchlist", "listings": request.user.merchant.watchlist.all()})

def category(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    return render(request, "commerce/index.html", {
        "title": f"{cat.name} listings", 
        "listings": Listing.objects.filter(category=cat, winner=None)
        })

def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    context = {"listing": listing}

    if request.user.is_authenticated:
        context['commentForm'] = CommentForm()

    return render(request, "commerce/listing.html", context)

def merchant(request, merchant_id):
    merchant = get_object_or_404(Merchant, pk=merchant_id)
    return render(request, "commerce/merchant.html", {"merchant": merchant})

@login_required
def new_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.merchant = request.user.merchant
            listing.save()
            form.save_m2m()
            return redirect('commerce:listing', listing_id=listing.id)
        else: 
            return render(request, 'commerce/listing_form.html', {
                'form': form,
                'action': 'new',
                'errors': form.errors
            })

    form = ListingForm()
    return render(request, 'commerce/listing_form.html', {"form": form, "action": "new"})

@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
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
    #else:
        #raise IntegrityError
    return redirect("commerce:listing", listing_id=listing_id)

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
'''
