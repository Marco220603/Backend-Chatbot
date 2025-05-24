from django.contrib import admin
from .models import Student,WhatsAppUserStudent,Ticket, Admin
# Register your models here.

admin.site.register(Student)
admin.site.register(WhatsAppUserStudent)
admin.site.register(Ticket)
admin.site.register(Admin)