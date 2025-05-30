# Generated by Django 4.2.20 on 2025-05-01 22:09

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=50)),
                ('full_name', models.CharField(max_length=100)),
                ('cellphone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('career', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_upc', models.CharField(max_length=10, unique=True)),
                ('full_name', models.CharField(max_length=100)),
                ('career', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='WhatsAppUserStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=20, unique=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.student')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('type_ticket', models.CharField(choices=[('technical', 'Tecnico'), ('academic', 'Academico'), ('other', 'Otro')], default='other', max_length=20)),
                ('state', models.CharField(choices=[('pending', 'Pendiente'), ('in_progress', 'En Progreso'), ('resolved', 'Resuelto'), ('closed', 'Cerrado')], default='pending', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Baja'), ('medium', 'Media'), ('high', 'Alta')], default='low', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('atendido_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.admin')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.whatsappuserstudent')),
            ],
        ),
    ]
