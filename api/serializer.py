from rest_framework import serializers
from .models import FeedbackGPT, Student, Ticket

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    student_name  = serializers.CharField(source='student.student.full_name', read_only=True)
    atendido_name = serializers.CharField(source='atendido_por.full_name', read_only=True)
    
    class Meta:
        model  = Ticket
        fields = '__all__'

class FeedbackGPTSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackGPT
        fields = "__all__"