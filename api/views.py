from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import generics
from .serializer import FeedbackGPTSerializer, StudentSerializer, TicketSerializer
from .models import FeedbackGPT, Student, WhatsAppUserStudent,Ticket
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView


# Create your views here.
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
class FeedbackGPTCreateView(generics.CreateAPIView):
    queryset = FeedbackGPT.objects.all()
    serializer_class = FeedbackGPTSerializer
    
@api_view(['POST'])
def validar_codigo_estudiante(request):
    codigo = request.data.get('codigo_estudiante')
    numero_celular = request.data.get('numero_celular')
    
    # 1. -- VALIDAR ENTRADA --
    # Validar que se haya enviado un codigo de estudiante
    if not codigo:
        return Response({'error': 'No se recibió código de estudiante.'}, status=400)

    # Validar que se haya enviado un numero de celular
    if not numero_celular:
        return Response({'error': 'No se recibió número de celular'}, status=400)
    
    # 2. -- BUSCAR ESTUDIANTE --
    try:
        estudiante = Student.objects.get(code_upc = codigo)
    except Student.DoesNotExist:
        return Response({'error': 'Código de estudiante no encontrado.'}, status=404)

    # 3. -- VINCULAR / ACTUALIZAR WhatsAppUserStudent --
    # ─── 3.1. Localizar (si existe) el registro del teléfono ───
    wa_user = WhatsAppUserStudent.objects.filter(phone_number=numero_celular).first()
    
    if wa_user:
        # a) Si ya pertenece al mismo estudiante → solo continúa
        if wa_user.student == estudiante:
            pass
        else:
            # b) Estaba ligado a OTRO estudiante → transferir
            wa_user.student = estudiante
            wa_user.save(update_fields=['student'])
    else:
        # c) El teléfono no existía → crear
        wa_user = WhatsAppUserStudent.objects.create(
            student=estudiante,
            phone_number=numero_celular
        )
        
    # ─── 3.2. Garantizar que el estudiante no tenga otro teléfono ──
    WhatsAppUserStudent.objects.exclude(pk=wa_user.pk).filter(student=estudiante).delete()
    # 4. -- RESPUESTA --
    return Response(
        {
            'message': 'Estudiante validado y número vinculado.',
            'whatsapp_user_id': wa_user.id,
            'telefono': wa_user.phone_number,
            'nombre': wa_user.student.full_name,
            'estado': wa_user.student.is_active
        },
        status=200
    )

# Constantes RASA
RASA_REST_WEBHOOK = 'http://localhost:5005/webhooks/rest/webhook'
RASA_MODEL_PARSE = 'https://a084-200-0-118-230.ngrok-free.app/webhooks/rest/webhook'

@api_view(['POST'])
def consulta_usuario2(request):
    user_message = request.data.get('message')

    if not user_message:
        return Response({'error': 'No se recibió ningún mensaje.'}, status=400)

    try:
        # Llamar a Rasa
        payload = {
            "message": user_message
        }
        rasa_response = requests.post(RASA_REST_WEBHOOK, json=payload, timeout=10)
        rasa_response.raise_for_status()

        data = rasa_response.json()
        print(data)
        if data:
            respuesta_texto = data[0].get('text', 'No entendí tu pregunta.')  # tomamos el primer mensaje
        else:
            respuesta_texto = 'No recibí respuesta del servidor.'

        return Response({'response': respuesta_texto})

    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def consulta_usuario(request):
    user_message = request.data.get('message')

    if not user_message:
        return Response({'error': 'No se recibió ningún mensaje.'}, status=400)

    try:
        # Paso 1: Analizar el mensaje con model/parse
        parse_payload = {"text": user_message}
        parse_response = requests.post(RASA_MODEL_PARSE, json=parse_payload, timeout=10)
        parse_response.raise_for_status()

        parse_data = parse_response.json()
        intent_name = parse_data.get('intent', {}).get('name', 'nlu_fallback')
        confidence = parse_data.get('intent', {}).get('confidence', 0)

        print(f"Intent detectado: {intent_name} (Confianza: {confidence})")

        # Paso 2: Validar el intent
        if intent_name == 'nlu_fallback':
            # Si es fallback, responder que no se entendió
            mensaje_no_entendido = "❌ No entendí tu consulta. ¿Podrías reformularla?"
            return Response({
                'response': mensaje_no_entendido,
                'source': 'rasa_fallback'
            })

        else:
            # Si el intent es válido, llamar normalmente a Rasa
            rasa_payload = {"message": user_message}
            rasa_response = requests.post(RASA_REST_WEBHOOK, json=rasa_payload, timeout=10)
            rasa_response.raise_for_status()

            data = rasa_response.json()
            if data:
                respuesta_texto = data[0].get('text', 'No entendí tu pregunta.')
            else:
                respuesta_texto = 'No recibí respuesta del servidor.'

            return Response({
                'response': respuesta_texto,
                'source': 'rasa'
            })

    except Exception as e:
        print(f"Error en consulta_usuario: {e}")
        return Response({'error': str(e)}, status=500)

# Crear Ticket
@api_view(['POST'])
def crearTicket(request):
    titulo = request.data.get('titulo')
    celular = request.data.get('celular')
    descripcion = request.data.get('descripcion')
    tipo = request.data.get('tipo')

    #1. -- VALIDAR ENTRADA --
    if not titulo or not celular or not descripcion or not tipo:
        return Response({'error': 'Faltan datos para crear el ticket.'}, status=400)
    
    #2. -- BUSCAR ESTUDIANTE --
    try:
        estudiante = WhatsAppUserStudent.objects.get(phone_number=celular)
    except WhatsAppUserStudent.DoesNotExist:
        return Response({'error': 'Numero de celular no encontrado.'},status=400)
    
    #3. -- CREAR TICKET --
    ticket = Ticket.objects.create(
        student = estudiante,
        subject = titulo,
        description = descripcion,
        type_ticket = tipo,
        
    )
    
    return Response(
        {
            'message': 'Ticket creado exitosamente.',
            'ticket_id': ticket.id,
            'titulo': ticket.subject,
            'descripcion': ticket.description,
            'tipo': ticket.type_ticket,
            'estado': ticket.state
        },
        status=201
    )

class TicketPlainListView(ListAPIView):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.select_related('student', 'atendido_por')
    pagination_class = None        # 🔑  sin paginación
    filter_backends  = []          # 🔑  sin filtros

class TicketDetailView(RetrieveUpdateAPIView):
    queryset = Ticket.objects.select_related('student', 'atendido_por')
    serializer_class = TicketSerializer   # soporta GET y PATCH