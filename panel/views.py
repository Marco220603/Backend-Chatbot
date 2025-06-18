from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from api.models import Ticket, Student, WhatsAppUserStudent, Admin
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q

# Create your views here.
@login_required
def home(request):
    return render(request, 'home.html',{})


def signin(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': AuthenticationForm()})

    # POST -----------------------
    username = request.POST.get('username')
    password = request.POST.get('password')

    # Valida que ambos campos vengan
    if not all([username, password]):
        return render(request, 'login.html', {
            'form': AuthenticationForm(),
            'error': 'Debes completar usuario y contraseña.'
        })

    user = authenticate(request, username=username, password=password)

    if user is None:
        # Credenciales incorrectas
        return render(request, 'login.html', {
            'form': AuthenticationForm(),
            'error': 'Usuario o contraseña incorrectos'
        })

    # Credenciales correctas → login y redirige
    login(request, user)
    return redirect('home')

def signout(request):
    logout(request)
    return redirect('login')

def verTickets(request):
    return render(request, 'tickets.html')

def verFeedback(request):
    return render(request, 'feedback.html')