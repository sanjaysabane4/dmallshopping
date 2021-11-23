from django import forms
from django.contrib.messages.api import success
from django.shortcuts import redirect, render
from django.views import View
from .models import Product, Cart, Customer, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

def search(request):
    if 'q' in request.GET:
        q=request.GET['q']
        data = Product.objects.filter(title__icontains=q)
    else:
        data = Product.objects.all()
    return render(request, 'app/search.html', {'data':data})


class ProductView(View):
    def get(self, request):
        totalitem = 0
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        laptops = Product.objects.filter(category='L')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/home.html', {'topwears':topwears, 'bottomwears':bottomwears, 'mobiles':mobiles, 'laptops':laptops, 'totalitem':totalitem})


class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        totalitem = 0
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'app/productdetail.html', {'product':product, 'item_already_in_cart':item_already_in_cart, 'totalitem':totalitem})

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')


@login_required
def buy_now(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/checkout')


@login_required
def show_cart(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 50.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]

        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                totalamount = amount + shipping_amount
            return render(request, 'app/addtocart.html', {'carts':cart, 'totalamount':totalamount, 'amount':amount, 'totalitem':totalitem})
        else:
            return render(request, 'app/emptycart.html')


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 50.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        
        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 50.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        
        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 50.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        
        data = {
            'amount':amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)



def buy_now(request):
 return render(request, 'app/buynow.html')

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))        
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary', 'totalitem':totalitem})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name1 = form.cleaned_data['name']
            locality1 = form.cleaned_data['locality']
            city1 = form.cleaned_data['city']
            zipcode1 = form.cleaned_data['zipcode']
            state1 = form.cleaned_data['state']
            reg = Customer(user = usr, name = name1, locality = locality1, city = city1, zipcode = zipcode1, state = state1)
            reg.save()
            messages.success(request, 'Congrulations!! Profile Updated Successfully')
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})

@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/address.html', {'add':add, 'active':'btn-primary', 'totalitem':totalitem})


def mobile(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == "redmi" or data == "samsung" or data == "apple":
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == "below":
        mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=10000)
    elif data == "above":
        mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=10000)
    return render(request, 'app/mobile.html', {'mobiles':mobiles, 'totalitem':totalitem})


def laptop(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    if data == None:
        laptop = Product.objects.filter(category='L')
    elif data == "HP" or data == "Lenovo" or data == "Dell" or data == 'Acer':
    # elif data.lower() in ["redmi", "samsung", "apple"]:
        laptop = Product.objects.filter(category='L').filter(brand=data)
    elif data == "below":
        laptop = Product.objects.filter(category='L').filter(discounted_price__lt=40000)
    elif data == "above":
        laptop = Product.objects.filter(category='L').filter(discounted_price__gt=40000)
    return render(request, 'app/laptop.html', {'laptop':laptop, 'totalitem':totalitem})    


def topwear(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    if data == None:
        top = Product.objects.filter(category='TW')
    elif data == 'top' or data == 'top brand':
        top = Product.objects.filter(category='TW').filter(brand=data)
    elif data == "below":
        top = Product.objects.filter(category='TW').filter(discounted_price__lt=1000)
    elif data == "above":
        top = Product.objects.filter(category='TW').filter(discounted_price__gt=1000)    
    return render(request, 'app/topwear.html', {'top':top, 'totalitem':totalitem})

def bottomwear(request, data=None):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))

    if data == None:
        bottom = Product.objects.filter(category='BW')
    elif data == 'bottom' or data == 'bottom brand':
        bottom = Product.objects.filter(category='BW').filter(brand=data)
    elif data == "below":
        bottom = Product.objects.filter(category='BW').filter(discounted_price__lt=1000)
    elif data == "above":
        bottom = Product.objects.filter(category='BW').filter(discounted_price__gt=1000)    
    return render(request, 'app/bottomwear.html', {'bottom':bottom, 'totalitem':totalitem})

def login(request):
 return render(request, 'app/login.html')

# def customerregistration(request):
#  return render(request, 'app/customerregistration.html')

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form':form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congrulations!! Registration Successfully")
            form.save()
        return render(request, 'app/customerregistration.html', {'form':form})


@login_required
def checkout(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    totalamount = 0.0
    shipping_amount = 50.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        totalamount = amount + shipping_amount
    return render(request, 'app/checkout.html', {'add':add, 'totalamount':totalamount, 'cart_items':cart_items, 'totalitem':totalitem})

@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/orders.html', {'order_placed':op, 'totalitem':totalitem})

@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")