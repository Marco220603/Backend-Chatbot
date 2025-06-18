from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models 
class Student(models.Model):
    code_upc = models.CharField(max_length=15, unique=True) # ejm: u20201f583 u202111c52
    full_name = models.CharField(max_length=100) # ejm: Ponce Boza Marco Andre
    career = models.CharField(max_length=50) # ejm: Ingenieria de Sistemas de Informacion
    is_active = models.BooleanField(default=False) # ejm: True

# La clase User ya contiene estos atributos:
# - username, password (encriptada), email, first_name y last_name, is_staff, is_superuser, etc.
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    cellphone = models.CharField(max_length=20)
    career = models.CharField(max_length=50)
    is_superAdmin = models.BooleanField(default=False)

class WhatsAppUserStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, unique=True)
    last_date_update = models.DateTimeField(auto_now=True)

class Ticket(models.Model):
    ESTADO_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('resolved', 'Resuelto'),
        ('closed', 'Cerrado')
    ]
    
    TIPO_CHOICES = [
        ('Problemas de comunicación', 'Problemas de comunicación'),
        ('Errores en el formulario', 'Errores en el formulario'),
        ('Documentación incompleta', 'Documentación incompleta')
    ]
    
    PRIORIDAD_CHOICES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta')
    ]
    
    #Relaciones
    student = models.ForeignKey(WhatsAppUserStudent, on_delete=models.CASCADE) # Relacion con el modelo Student
    atendido_por = models.ForeignKey(Admin, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Tickets
    subject = models.CharField(max_length=100) # ejm: Problema con un documento
    description = models.TextField() # ejm: No puedo abrir el documento
    type_ticket =  models.CharField(max_length=50, choices=TIPO_CHOICES,default='other')
    state = models.CharField(max_length=20, choices=ESTADO_CHOICES,default='pending')
    priority = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES,default='Baja')
    
    #Fechas
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

class Feedback(models.Model):
    user_message = models.TextField()  # Consulta del usuario
    bot_response = models.TextField()  # Respuesta del bot
    timestamp = models.DateTimeField(auto_now_add=True)  # Fecha de creación

    def __str__(self):
        return f"Consulta: {self.user_message} | Respuesta: {self.bot_response}"