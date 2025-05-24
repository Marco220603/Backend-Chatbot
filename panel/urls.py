from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.signin, name='login'),
    path('logout/', views.signout, name='logout'),
    path('tickets/', views.verTickets, name='tickets')
]