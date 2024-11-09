from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Property, Booking
from .forms import PropertyForm
from django.urls import reverse

# 1. Index Page
def index(request):
    return render(request, 'index.html')

# 2. User Registration
def Registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'signup.html')

        user = User.objects.create_user(
            username=username, 
            first_name=first_name,
            last_name=last_name, 
            email=email, 
            password=password
        )
        user.save()
        messages.success(request, "Account created successfully.")
        return redirect('login')

    return render(request, 'signup.html')

# 3. Login
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

def Login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if a user with the given username exists
        if not User.objects.filter(username=username).exists():
            messages.error(request, "No user found with that username.")
            return render(request, 'login.html')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html')

    return render(request, 'login.html')


# 4. Logout
def Logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('/')

# 5. Homepage (after login)
@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')

# 6. Property Listings for Users
def Properties(request):
    properties = Property.objects.all()
    context = {'properties': properties}
    return render(request, 'property.html', context)

# 7. Property Details
@login_required
def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    booking = None

    if request.user.is_authenticated:
        booking = Booking.objects.filter(property=property, client=request.user).first()
    
    is_available = property.is_available and (booking is None or booking.approval_status == 'rejected')

    context = {
        'property': property,
        'booking': booking,
        'is_available': is_available,
    }
    
    return render(request, 'property_details.html', context)

# 8. Book Property
@login_required
def book_property(request, pk):
    property = get_object_or_404(Property, pk=pk, is_available=True)
    existing_booking = Booking.objects.filter(
        property=property, client=request.user, approval_status__in=['pending', 'approved']
    ).first()
    
    if existing_booking:
        messages.warning(request, "You already have a pending or approved booking for this property.")
        return redirect('property_detail', pk=property.pk)

    Booking.objects.create(property=property, client=request.user, is_booked=True, approval_status='pending')
    messages.success(request, "Your booking request has been submitted and is pending approval.")
    return redirect(reverse('property_detail', args=[property.pk]))

# 9. Seller Dashboard
@login_required
def seller_dashboard(request):
    seller_id = request.user.id
    properties = Property.objects.filter(seller_id=seller_id)
    
    context = {
        'seller_id': seller_id,
        'properties': properties
    }
    return render(request, 'seller_dashboard.html', context)

# 10. Add Property
@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.seller = request.user
            is_available = request.POST.get('is_available')
            property.is_available = True if is_available == "on" else False
            property.save()
            return redirect('allproperties')
    else:
        form = PropertyForm()
    return render(request, 'add_property.html', {'form': form})

# 11. Update Property
@login_required
def update_property(request, pk):
    property_instance = get_object_or_404(Property, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property_instance)
        if form.is_valid():
            form.save()
            return redirect('seller_dashboard')
    else:
        form = PropertyForm(instance=property_instance)

    return render(request, 'update_property.html', {'form': form})

# 12. Delete Property
@login_required
def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)

    if request.method == 'POST':
        property.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('seller_dashboard')
    
    return render(request, 'delete_property.html', {'property': property})

# 13. Seller Bookings
@login_required
def seller_bookings(request):
    properties = Property.objects.filter(seller=request.user).select_related('seller')
    bookings = Booking.objects.filter(property__in=properties).select_related('property', 'client')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'seller_bookings.html', context)

# 14. Property List for Seller
@login_required
def property_list(request):
    properties = Property.objects.filter(seller=request.user)
    return render(request, 'properties/property_list.html', {'properties': properties})

# 15. Approve Booking
@login_required
def approve_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, property__is_booked=False)

    if request.method == "POST":
        approval_status = request.POST.get("status")
        
        if approval_status in ["approved", "rejected"]:
            booking.approval_status = approval_status
            
            if approval_status == "approved":
                booking.property.is_booked = True
                booking.property.save()

            booking.save()
            messages.success(request, f"The booking has been {approval_status} successfully.")
            return redirect('/property')
        else:
            messages.error(request, "Invalid status selected.")

    return render(request, 'approve_booking.html', {'booking': booking})

# 16. Update Booking Status
@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id, property__seller=request.user)
    if status in ['approved', 'rejected']:
        booking.approval_status = status
        booking.save()
    return redirect('seller_bookings')

# 17. Booking List (Admin)
def booking_list(request):
    bookings = Booking.objects.all()
    return render(request, 'booking_list.html', {'bookings': bookings})
