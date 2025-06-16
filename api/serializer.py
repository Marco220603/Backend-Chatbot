from rest_framework import serializers
from .models import Student, Ticket, User, Admin, WhatsAppUserStudent

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['code_upc', 'full_name', 'career', 'is_active']

class WhatsAppUserSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    class Meta:
        model = WhatsAppUserStudent
        fields = ['student', 'phone_number','last_date_update']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Admin
        fields = ['id', 'cellphone', 'career', 'user']

class TicketSerializer(serializers.ModelSerializer):
    atendido_por = AdminSerializer()
    student = WhatsAppUserSerializer()
    class Meta:
        model = Ticket
        fields = '__all__'