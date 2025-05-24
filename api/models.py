from django.db import models
from django.utils import timezone

# Create your models 
# Heññp
class Student(models.Model):
    code_upc = models.CharField(max_length=15, unique=True) # ejm: u20201f583 u202111c52
    full_name = models.CharField(max_length=100) # ejm: Ponce Boza Marco Andre
    career = models.CharField(max_length=50) # ejm: Ingenieria de Sistemas de Informacion
    is_active = models.BooleanField(default=False) # ejm: True

class Admin(models.Model):
    username = models.CharField(max_length=50, unique=True) 
    password = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    cellphone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)
    career = models.CharField(max_length=50)

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
        ('technical', 'Tecnico'),
        ('academic', 'Academico'),
        ('other', 'Otro')
    ]
    
    PRIORIDAD_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta')
    ]
    
    #Relaciones
    student = models.ForeignKey(WhatsAppUserStudent, on_delete=models.CASCADE) # Relacion con el modelo Student
    atendido_por = models.ForeignKey(Admin, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Tickets
    subject = models.CharField(max_length=100) # ejm: Problema con un documento
    description = models.TextField() # ejm: No puedo abrir el documento
    type_ticket =  models.CharField(max_length=20, choices=TIPO_CHOICES,default='other')
    state = models.CharField(max_length=20, choices=ESTADO_CHOICES,default='pending')
    priority = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES,default='low')
    
    #Fechas
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

class FeedbackGPT(models.Model):
    SATISFACTION_CHOICES = [
        ('positive', 'Positiva'),
        ('negative', 'Negativa'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ]
    user_message = models.TextField()
    bot_response = models.TextField()
    satisfaction = models.CharField(max_length=10, choices=SATISFACTION_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Feedback: {self.user_message[:30]}..."