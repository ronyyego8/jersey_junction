import django
from django.contrib.auth.models import User
from jersey_app.models import Address, Cart, Category, Order, Product , Favorite
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
import json
import base64
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils import timezone
from .models import Payment
import requests
from django.http import JsonResponse





# Create your views here.  

def home(request):    
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    categories_menu = Category.objects.filter(is_active=True)
    
    # Calculate cart \\
    cart_items_count = 0
    if request.user.is_authenticated:
        cart_items_count = Cart.objects.filter(user=request.user).count()
    

    context = {
        'categories': categories,
        'products': products,
        'categories_menu': categories_menu,
        'cart_items_count': cart_items_count,
         
    }
    return render(request, 'store/index.html', context)

def about(request):
    # Calculate cart items count
    cart_items_count = 0
    if request.user.is_authenticated:
        cart_items_count = Cart.objects.filter(user=request.user).count()

    return render(request, 'store/about.html', {'cart_items_count': cart_items_count})


def contact(request):
    # Calculate cart items count
    cart_items_count = 0
    if request.user.is_authenticated:
        cart_items_count = Cart.objects.filter(user=request.user).count()

    return render(request, 'store/contact.html', {'cart_items_count': cart_items_count})




def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    context = {
        'product': product,
        'related_products': related_products,

    }
    return render(request, 'store/detail.html', context)

def all_products(request):
    # Retrieve all products from the database
    products = Product.objects.all()
    
    # Calculate cart items count
    cart_items_count = 0
    if request.user.is_authenticated:
        cart_items_count = Cart.objects.filter(user=request.user).count()
    
    # Pass the products and cart items count to the template for rendering
    return render(request, 'store/all_products.html', {'products': products, 'cart_items_count': cart_items_count})

def all_categories(request):
    # Retrieve all active categories
    categories = Category.objects.filter(is_active=True)

    # Calculate cart items count
    cart_items_count = 0
    if request.user.is_authenticated:
        cart_items_count = Cart.objects.filter(user=request.user).count()

    # Pass categories and cart_items_count to the template
    return render(request, 'store/categories.html', {'categories': categories, 'cart_items_count': cart_items_count})


def category_products(request, slug):
    # Retrieve the category based on the slug
    category = get_object_or_404(Category, slug=slug)

    # Retrieve products belonging to the category
    products = Product.objects.filter(is_active=True, category=category)

    # Retrieve all active categories for the menu
    categories = Category.objects.filter(is_active=True)

    # Calculate cart items count
    cart_items_count = 0
    if request.user.is_authenticated:
        cart_items_count = Cart.objects.filter(user=request.user).count()

    # Pass category, products, categories, and cart_items_count to the template
    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'store/category_products.html', context)




def get_favorite_count(user):
    if user.is_authenticated:
        return Favorite.objects.filter(user=user).count()
    else:
        return 0

def navbar(request):
    cart_items_count = Cart.objects.filter(user=request.user).count() 
    favorite_items_count = get_favorite_count(request.user)
    return render(request, 'navbar.html', {'cart_items_count': cart_items_count, 'favorite_items_count': favorite_items_count})

def favorites(request):
    favorites = Favorite.objects.filter(user=request.user)
    context = {'favorites': favorites}
    return render(request, 'favorites.html', context)




# Authentication Starts Here

class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})
        

@login_required
@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    
    # Calculate cart items count
    cart_items_count = 0
    if request.user.is_authenticated:
        cart_items_count = Cart.objects.filter(user=request.user).count()

    context = {
        'addresses': addresses,
        'orders': orders,
        'cart_items_count': cart_items_count,  # Pass cart items count to the template context
    }
    return render(request, 'account/profile.html', context)

def my_view(request):
    # Update last access time to keep the session alive
    request.session.modified = True
    request.session.set_expiry(600)  # Extend session expiry to 10 minutes (600 seconds)

    

    # For example:
    if request.user.is_authenticated:
        

        # Logout the user if the session has expired
        if 'last_activity' in request.session:
            last_activity = request.session['last_activity']
            if timezone.now() - last_activity > timezone.timedelta(minutes=10):
                logout(request)
                # Optionally, you can redirect the user to a login page or any other page after logout
                return redirect('login')
        request.session['last_activity'] = timezone.now()

        # Continue with your view logic for authenticated users...
    else:
        # Your logic for unauthenticated users here...
        pass

    # Render a template as the response
    return render(request, 'index.html')


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is already in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()
    
    return redirect('jersey_app:cart')


@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Calculate total amount
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    for cart_product in cart_products:
        temp_amount = cart_product.quantity * cart_product.product.price
        amount += temp_amount

    # Get count of items in the cart
    cart_items_count = cart_products.count()

    # Customer Addresses
    addresses = Address.objects.filter(user=user)
    print('Addresses', addresses)

    context = {
        'cart_products': cart_products,
        'cart_items_count': cart_items_count,  
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
        
    }
    return render(request, 'store/cart.html', context)



@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('jersey_app:cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('jersey_app:cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('jersey_app:cart')


@login_required
def checkout(request):
    user = request.user
    address_id = request.GET.get('address')  # Retrieve address ID from URL query parameter
    print("Address ID:", address_id)

    if not address_id:
        # If address_id is not provided, redirect back to cart with an error message
        messages.error(request, "Please select an address before proceeding to checkout.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/cart/'))

    # Check if the provided address belongs to the logged-in user
    address = get_object_or_404(Address, id=address_id, user=user)

    # Get the user's cart items
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        # If the cart is empty, redirect back to cart with an error message
        messages.error(request, "Your cart is empty.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/cart/'))

    # Calculate total amount, shipping amount, and total amount
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    for cart_item in cart_items:
        temp_amount = cart_item.quantity * cart_item.product.price
        amount += temp_amount

    total_amount = amount + shipping_amount

    # Calculate cart items count
    cart_items_count = cart_items.count()

    # Render the checkout page with necessary data
    context = {
        'address': address,
        'cart_items': cart_items,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': total_amount,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'store/checkout.html', context)



@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    cart_items_count = Cart.objects.filter(user=request.user).count()
    return render(request, 'store/orders.html', {'orders': all_orders, 'cart_items_count': cart_items_count})

@login_required
def process_cod(request):
    if request.method == 'POST':
        selected_address_id = request.POST.get('address')
        if not selected_address_id:
            # Handle case where no address is selected
            messages.error(request, 'Please select a shipping address.')
            return redirect('jersey_app:cart')

        # Fetch the selected address
        selected_address = Address.objects.get(id=selected_address_id)

        # Fetch the user's cart items
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            # Handle case where the cart is empty
            messages.error(request, 'Your cart is empty.')
            return redirect('jersey_app:cart')

        # Create orders for each cart item
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                address=selected_address,
                product=item.product,
                quantity=item.quantity,
                ordered_date=timezone.now(),
                status='Pending'
            )

        # Clear the user's cart
        cart_items.delete()

        # Redirect to the orders page
        return redirect('jersey_app:orders')

    return redirect('jersey_app:cart')

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('jersey_app:home')
    def post(self, request, *args, **kwargs):
        # Handle POST requests in the same way as GET requests
        return self.get(request, *args, **kwargs)
    



def get_access_token():
    consumer_key = 'IyK6KYxPLUzu6Y1d54OziQ51veQsSIZMSFZau0ANjRKsPQVA'
    consumer_secret = 'poDb4hGcOmQGeNHLMmymrPw8jktvDWovDi5LKXYflGsBOPZkFuOuzB53Rocm4AAT'
    auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    
    credentials = f'{consumer_key}:{consumer_secret}'
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}'
    }
    
    response = requests.get(auth_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    else:
        print('Failed to obtain access token:', response.status_code, response.text)
        return None

@login_required
def initiate_payment(request):
    try:
        amount = request.GET.get('amount')
        phone_number = request.GET.get('phone_number')

        print('Amount Received:', amount)
        print('Phone Number:', phone_number)

        access_token = get_access_token()
        if not access_token:
            return JsonResponse({'message': 'Failed to obtain access token'}, status=500)
        print('Access Token:', access_token)

        if not amount or not amount.isdigit() or int(amount) <= 0:
            return JsonResponse({'message': 'Invalid amount'}, status=400)

        if not phone_number or len(phone_number) != 10 or not phone_number.isdigit():
            return JsonResponse({'message': 'Invalid phone number'}, status=400)
        
        phone_number = '254' + phone_number[1:]

        business_short_code = '174379'
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

        payload = {
            'BusinessShortCode': business_short_code,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': phone_number,
            'PartyB': business_short_code,
            'PhoneNumber': phone_number,
            'CallBackURL': 'http://127.0.0.1:8000/mpesa-callback/',
            'AccountReference': 'JJSOFTWARES',
            'TransactionDesc': 'Payment for Jersey Junction',
        }

        print('Payload:', json.dumps(payload, indent=4))

        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }

        # Print headers and payload before sending the request
        print('Headers:', headers)
        print('Sending POST request to Safaricom API...')

        response = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', json=payload, headers=headers)

        # Print response details
        print('Response Status Code:', response.status_code)
        print('Response Text:', response.text)

        if response.status_code == 200:
            data = response.json()
            payment = Payment.objects.create(
                transaction_id=data.get('CheckoutRequestID'),
                amount=amount,
                status='pending'
            )
            print('Payment:', payment)
            return JsonResponse({'message': 'Payment successful', 'data': data})
        else:
            try:
                error_message = response.json().get('errorMessage', 'Payment failed')
            except json.JSONDecodeError:
                error_message = 'Payment failed with status code ' + str(response.status_code)
            print('Error Message:', error_message)
            return JsonResponse({'message': error_message}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        print('Request Exception:', e)
        return JsonResponse({'message': 'An error occurred while processing the payment'}, status=500)
    except Exception as e:
        print('General Exception:', e)
        return JsonResponse({'message': 'An internal server error occurred'}, status=500)

@login_required
def mpesa_callback(request):
    try:
        print('M-PESA Callback Received:', request.method)
        if request.method == 'POST':
            data = json.loads(request.body)
            print('Callback Data:', json.dumps(data, indent=4))

            transaction_id = data.get('TransactionID')
            result_code = data.get('ResultCode')
            result_desc = data.get('ResultDesc')
            
            try:
                payment = Payment.objects.get(transaction_id=transaction_id)
                payment.status = 'received'
                payment.save()
                print('Payment Status Updated:', payment.status)
            except Payment.DoesNotExist:
                print('Payment with Transaction ID', transaction_id, 'not found.')

            return HttpResponse(status=200)

        print('Invalid Request Method:', request.method)
        return HttpResponse(status=400)
    except Exception as e:
        print('Callback Exception:', e)
        return HttpResponse(status=500)
    
def shop(request):
    return render(request, 'store/shop.html')





def test(request):
    return render(request, 'store/test.html')
