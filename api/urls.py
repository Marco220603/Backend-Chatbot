from django.urls import path, include
from rest_framework import routers
from api import views
from .views import TicketPlainListView, TicketDetailView

router = routers.DefaultRouter()

router.register(r'student', views.StudentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('validar/', views.validar_codigo_estudiante,),
    path('consulta/', views.consulta_usuario,),
    path('crear_ticket/',views.crearTicket),
    path('tickets-all/', TicketPlainListView.as_view(), name='tickets-all'),
    path('tickets/<int:pk>/', TicketDetailView.as_view())
]