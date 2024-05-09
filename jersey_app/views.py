import django
from django.contrib.auth.models import User
from jersey_app.models import Address, Cart, Category, Order, Product , Favorite
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone





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
    return render (request,'store/about.html')

def contact(request):
    return render(request,'store/contact.html')



def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    context = {
        'product': product,
        'related_products': related_products,

    }
    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True)
    context = {
        'category': category,
        'products': products,
        'categories': categories,
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
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})

def my_view(request):
    # Update last access time to keep the session alive
    request.session.modified = True
    request.session.set_expiry(300)  # Extend session expiry to 5 minutes (300 seconds)

    # Your view logic here...
    # This might include checking if the user is authenticated, accessing user-related data, etc.

    # For example:
    if request.user.is_authenticated:
        # Your authenticated user logic here...

        # Logout the user if the session has expired
        if 'last_activity' in request.session:
            last_activity = request.session['last_activity']
            if timezone.now() - last_activity > timezone.timedelta(minutes=1):
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

    # Check whether the Product is alread in Cart or Not
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
    address_id = request.GET.get('address')
    
    address = get_object_or_404(Address, id=address_id)
    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(user=user, address=address, product=c.product, quantity=c.quantity).save()
        # And Deleting from Cart
        c.delete()
    return redirect('jersey_app:orders')


@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    cart_items_count = Cart.objects.filter(user=request.user).count()
    return render(request, 'store/orders.html', {'orders': all_orders, 'cart_items_count': cart_items_count})

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('jersey_app:home')
    def post(self, request, *args, **kwargs):
        # Handle POST requests in the same way as GET requests
        return self.get(request, *args, **kwargs)



def shop(request):
    return render(request, 'store/shop.html')





def test(request):
    return render(request, 'store/test.html')
