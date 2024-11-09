from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('register/', views.Registration, name='register'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('seller_dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('add/', views.add_property, name='add_property'),
    path('update/<int:pk>/', views.update_property, name='update_property'), 
    path('delete/<int:pk>/', views.delete_property, name='delete_property'),

    path('property/', views.Properties, name='allproperties'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),  
    path('book_property/<int:pk>/', views.book_property, name='book_property'), 
    path('seller/bookings/', views.seller_bookings, name='seller_bookings'),
    path('seller/bookings/<int:booking_id>/<str:status>/', views.update_booking_status, name='update_booking_status'),
    path('bookings/<int:id>/approve/', views.approve_booking, name='approve_booking'),  # Kept this as id since it relates to the booking ID
    
]
