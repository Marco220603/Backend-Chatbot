from django.shortcuts import render
from rest_framework import viewsets
from .serializer import StudentSerializer, TicketSerializer
from .models import Student, WhatsAppUserStudent,Ticket, Admin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework import status
from random import choice
from django.shortcuts import get_object_or_404
from datetime import datetime


# Create your views here.
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
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
RASA_REST_WEBHOOK = 'https://bb3e-38-253-158-240.ngrok-free.app/webhooks/rest/webhook'
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
    
    prioridades = {
        "No puedo contactar a mi asesor especializado": "Alta",
        "No puedo contactar a mi coautor": "Alta",
        "Ingreso erróneo de código del alumno": "Media",
        "Error en el nombre del partner": "Media",
        "Error en el nombre del asesor especializado": "Baja",
        "No adjunté el documento firmado y aprobado por el asesor especializado": "Alta"
    }
    prioridad = prioridades.get(tipo, "Media")

    #1. -- VALIDAR ENTRADA --
    if not titulo or not celular or not descripcion or not tipo:
        return Response({'error': 'Faltan datos para crear el ticket.'}, status=400)
    
    #2. -- BUSCAR ESTUDIANTE --
    try:
        estudiante = WhatsAppUserStudent.objects.get(phone_number=celular)
    except WhatsAppUserStudent.DoesNotExist:
        return Response({'error': 'Numero de celular no encontrado.'},status=400)
    
    admin_random = choice(Admin.objects.all())
    
    #3. -- CREAR TICKET --
    ticket = Ticket.objects.create(
        student = estudiante,
        subject = titulo,
        description = descripcion,
        type_ticket = tipo,
        priority = prioridad,
        atendido_por = admin_random
    )
    
    # --- NOTIFICAR AL ADMIN POR WHATSAPP ---
    try:
        BUILDERBOT_URL = 'http://localhost:3008'
        FRONTEND_URL = 'http://127.0.0.1:8000/panel'
        # Formatear número para Baileys (sin +, con 51 al inicio)
        admin_number = admin_random.cellphone
        mensaje = (
            f"📢 *Nuevo Ticket #{ticket.id}*\n"
            f"👤 Estudiante: {estudiante.student.full_name} ({estudiante.phone_number})\n"
            f"🎫 Título: {ticket.subject}\n"
            f"📂 Tipo: {ticket.type_ticket}\n"
            f"⚡ Prioridad: {ticket.priority}\n"
            f"📝 Descripción: {ticket.description}\n\n"
            f"👉 Atendelo aquí: {FRONTEND_URL}/tickets/{ticket.id}"
        )

        requests.post(
            f"{BUILDERBOT_URL}/v1/messages",
            {
                "number": admin_number,
                "message":  mensaje
            }
        )
    except Exception as e:
        # Logealo; no queremos que el fallo de WhatsApp impida crear el ticket
        print(f"Error enviando WhatsApp: {e}")
    
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

@api_view(['POST'])
def consultarPais(request):
    pais = request.data.get('message')
    if not pais:
        return Response({'error': 'no se recibio ningun pais'}, status=400)
    try:
        respuesta = requests.get(f"https://restcountries.com/v3.1/name/{pais}")
        if respuesta.status_code != 200:
            return Response({'error': 'País no encontrado o error de la API'}, status=respuesta.status_code)    
        data = respuesta.json()
        print(data)
        pais_info = data[0]
        resultado = {
            "nombre": pais_info['name']['common'],
            "capital": pais_info.get('capital', ['Desconocida'])[0],
            "region": pais_info.get('region', 'Desconocida'),
            "poblacion": pais_info.get('population', 'Desconocida'),
            "bandera": pais_info['flags']['png']
        }
        return Response(resultado)
    except Exception as e:
        print(f"Error al consultar API externa: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_tickets(request):
    tickets = Ticket.objects.all().order_by('-id')
    serializer = TicketSerializer(tickets, many = True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_ticket_por_id(request, id):
    try:
        ticket = Ticket.objects.get(id=id)
    except Ticket.DoesNotExist:
        return Response({'error': 'Ticket no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TicketSerializer(ticket)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])               # solo admins logeados
def reply_ticket(request, id):
    message = request.data.get('message', '').strip()
    if not message:
        return Response({'error': 'Falta el mensaje.'}, status=400)

    ticket = get_object_or_404(Ticket, id=id)

    # optional: verificar que request.user sea el admin asignado
    # if request.user != ticket.atendido_por.user: ...

    # 1) Actualizar ticket
    ticket.state      = 'in_progress'
    ticket.updated_at = datetime.now().time()
    ticket.save()

    # 2) Formatear mensaje para WhatsApp
    admin_user   = ticket.atendido_por.user
    estudiante   = ticket.student
    numero_alumno = estudiante.phone_number
    texto = (
        f"✅ *Respuesta a tu Ticket #{ticket.id}*\n"
        f"👨‍💼 Administrador: {admin_user.first_name} {admin_user.last_name}\n"
        f"🎫 Título: {ticket.subject}\n"
        f"💬 Respuesta:\n{message}\n\n"
    )

    # 3) Llamar a BuilderBot
    BUILDERBOT_URL = 'http://localhost:3008'
    try:
        requests.post(
            f"{BUILDERBOT_URL}/v1/sendAnswer",
            json={
                "number": numero_alumno,
                "message": texto
            },
            timeout=5
        )
    except Exception as e:
        print('Error enviando WhatsApp:', e)

    return Response({'detail': 'Respuesta enviada y ticket actualizado.'}, status=200)