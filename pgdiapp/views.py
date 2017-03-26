from django.shortcuts import render, redirect, render_to_response 
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required

from .forms import UserProfileForm, RespuestaForm
from .models import User, Perfil, Pregunta, Respuesta, Taller, Clase, Modulo

from datetime import datetime
import socket

# Vistas

def index(request):
	return render(request, 'pgdiapp/index.html')

# Entrada al perfil
def perfil(request, user_name):
	alumno = Perfil.objects.get(user__username=user_name)
	modulo = Modulo.objects.get(cod=alumno.modulo)
	return render(request, 'pgdiapp/perfil.html', { 'alumno': alumno, 'modulo':modulo })

# Pre-registro de un nuevo alumno
def register(request):
	#ip = socket.gethostbyname_ex(socket.gethostname())[2][1]
	ip = socket.gethostbyname(socket.gethostname())
	hora = datetime.now().strftime('%H')
	modulo = obtener_modulo(ip, hora)
	if request.method == 'POST':
		uform = UserCreationForm(request.POST)
		pform = UserProfileForm(data = request.POST)
		if uform.is_valid() and pform.is_valid():
			user = uform.save(commit = False)
			profile = pform.save(commit = False)
			user.username = generar_username(profile.nombre,profile.apellido1,profile.apellido2)
			user.save()
			profile.user = user
			profile.save()
			return HttpResponseRedirect("/app/cuestionario/"+str(user.username))
	else:
		uform = UserCreationForm()
		pform = UserProfileForm()
	return render(request, 'pgdiapp/user_form.html', { 'uform': uform, 'pform': pform, 'modulo':modulo, 'ip':ip })

# Formularo de preguntas
def cuestionario(request, user_name):
	usuario = User.objects.get(username=user_name)
	perfil = Perfil.objects.get(user=usuario)
	preguntas = Pregunta.objects.get(modulo=perfil.modulo)
	respuestas = []
	if request.method == 'POST':
		respuestas = RespuestaForm(data = request.POST)
		if respuestas.is_valid():
			respuesta = respuestas.save(commit = False)
			respuesta.save()
		return HttpResponseRedirect("/app/perfil/"+perfil.user.username)
	else:
		respuestas = RespuestaForm()
	return render(request, 'pgdiapp/cuestionario.html', { 'alumno':perfil, 'preguntas':preguntas, 'respuestas':respuestas })

# Obtencion del modulo por taller
def obtener_modulo(ip, hora):
	if int(hora) > 15:
		es_nocturno = True
	else:
		es_nocturno = False
	try:
		modulo = Clase.objects.get(taller__numero=ip[8:9], modulo__nocturno=es_nocturno).modulo.cod
	except:
		modulo = 'desconocido'
	return modulo

# Generacion del nombre del usuario
def generar_username(nom, ap1, ap2):
	while nom.find(' ') > 0:
		nom = nom.replace(' ', '')
	while ap1.find(' ') > 0:
		ap1 = ap1.replace(' ', '')
	while ap2.find(' ') > 0:
		ap2 = ap2.replace(' ', '')
	return (nom+ap1[:2]+ap2[:2]).lower()

# Cambiar password (TODO)
def pwmod(request):
	return redirect('/app')

# Login (TODO)
def login(request):
	return redirect('/app')

# Logout
def logout_view(request):
	logout(request)
	return redirect('/app/logout_redirect')

def logoutr(request):
	return render(request, 'pgdiapp/logout.html')
