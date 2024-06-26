from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from .utils import *
import json
import datetime


# Create your views here.

def home(request):
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, 'home.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, 'cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, 'checkout.html', context)


def updateitem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]

    print("Action:", action)
    print("productId:", productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == "remove":
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("item was added", safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data["form"]["total"])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
    else:
        customer, order = guestOrder(data, request)

    total = float(data["form"]["total"])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,order=order,address=data['shipping']['address'],city=data['shipping']['city'],
            state=data['shipping']['state'],zipcode=data['shipping']['zipcode'],
        )
    return JsonResponse("order completed", safe=False)

def signup(request):
    context = {}
    return render(request,'signup.html',context)
def login(request):
    context = {}
    return render(request,'login.html',context)
def logout(request):
    context = {}
    return render(request,'logout.html',context)