from django.urls import path, include
from rest_framework import routers
from api import views

router = routers.DefaultRouter()

router.register(r'student', views.StudentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('validar/', views.validar_codigo_estudiante,),
    path('consulta/', views.consulta_usuario,),
    path('crear_ticket/',views.crearTicket),
    path('tickets/', views.listar_tickets, name='tickets-all'),
    path('consultar-pais/', views.consultarPais),
    path('tickets/<int:id>/', views.obtener_ticket_por_id, name='obtener_ticket_por_id'),
    path('tickets/<int:id>/reply/', views.reply_ticket),
    path("gpt_response/", views.gpt_response, name="gpt_response"),
    path('feedback/', views.feedback_list, name='feedback_list'),  # Listar feedbacks
    path('feedback/add/', views.feedback_add, name='feedback_add'),  # Agregar feedback
    path('feedback/edit/<int:feedback_id>/', views.feedback_edit, name='feedback_edit'),  # Editar feedback
    path('feedback/delete/<int:feedback_id>/', views.feedback_delete, name='feedback_delete'),  # Eliminar feedback

]