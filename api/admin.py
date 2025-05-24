from django.contrib import admin
from .models import FeedbackGPT, Student,WhatsAppUserStudent,Ticket, Admin
# Register your models here.

admin.site.register(Student)
admin.site.register(WhatsAppUserStudent)
admin.site.register(Ticket)
admin.site.register(Admin)

@admin.register(FeedbackGPT)
class FeedbackGPTAdmin(admin.ModelAdmin):
    list_display = ('user_message', 'satisfaction', 'status', 'created_at')
    list_filter = ('satisfaction', 'status')
    search_fields = ('user_message', 'bot_response')
    actions = ['approve_feedback', 'reject_feedback']

    def approve_feedback(self, request, queryset):
        queryset.update(status='approved')
    approve_feedback.short_description = "Aprobar feedback seleccionado"

    def reject_feedback(self, request, queryset):
        queryset.update(status='rejected')
    reject_feedback.short_description = "Rechazar feedback seleccionado"