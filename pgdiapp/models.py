#-*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, MaxLengthValidator, MinLengthValidator
from localflavor.es.forms import ESIdentityCardNumberField

# Modelos

class Taller(models.Model):
	cod = models.CharField(max_length=5, unique=True)
	numero = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(3)])
	info = models.TextField(default=None, blank=True, null=True)
	def __str__(self):
		return str(self.cod)
	class Meta:
		ordering = ["cod"]
		verbose_name_plural = "Talleres"

class Grado(models.Model):
	cod = models.CharField(max_length=5, unique=True)
	nombre = models.CharField(max_length=200, unique=True)
	gid = models.CharField(max_length=5, unique=True)
	nocturno = models.BooleanField(default=False)
	def __str__(self):
		return str(self.cod)
	class Meta:
		ordering = ["cod"]
		verbose_name_plural = "Grados"

class Clase(models.Model):
	grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
	taller = models.ForeignKey(Taller, on_delete=models.CASCADE)
	curso = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(2)])
	grupo = models.CharField(max_length=1, default='A')
	tarde = models.BooleanField(default=False)
	def __str__(self):
		return str(self.curso) + str(self.grupo) + ' ' + str(self.grado)
	class Meta:
		ordering = ["grado","curso","grupo","taller"]
		#unique_together = ('grado', 'taller')
		verbose_name_plural = "Clases"

class Perfil(models.Model):
	user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
	grado = models.ForeignKey(Grado, blank=False, null=True, on_delete=models.CASCADE)
	passwd =  models.CharField(max_length=500, blank=False, null=True)
	dni_regex = RegexValidator(regex=r'^[0-9]{8}[a-zA-Z]{1}$')
	dni = models.CharField(max_length=9, validators=[dni_regex], unique=True, blank=False, null=True)
	nombre = models.CharField(validators=[MinLengthValidator(2),MaxLengthValidator(50)], max_length=50, blank=False, null=True)
	apellido1 = models.CharField(validators=[MinLengthValidator(2),MaxLengthValidator(50)], max_length=50, blank=False, null=True)
	apellido2 = models.CharField(validators=[MinLengthValidator(2),MaxLengthValidator(50)], max_length=50, blank=False, null=True)
	tel_regex = RegexValidator(regex=r'^\+?1?\d{9}$')
	telefono = models.CharField(max_length=9, validators=[tel_regex], blank=False, null=True)
	email = models.EmailField(blank=False, null=True)
	fecha_nac = models.DateField(blank=False, null=True)
	cp_regex = RegexValidator(regex=r'^[0-9]{5}$')
	cp = models.CharField(max_length=5, validators=[cp_regex], null=True)
	direccion = models.CharField(max_length=100, null=True)
	localidad = models.CharField(max_length=50, null=True)
	provincia = models.CharField(max_length=50, null=True)
	comunidad = models.CharField(max_length=50, null=True)
	pais = models.CharField(max_length=50, null=True)
	validado = models.BooleanField(default=False)

	estudios = models.CharField(max_length=50, null=True, blank=False)
	trabajo = models.CharField(max_length=50, null=True, blank=True)

	def __str__(self):
		return str(self.user.username)
	class Meta:
		ordering = ["user"]
		verbose_name_plural = "Perfiles"

@python_2_unicode_compatible
class Pregunta(models.Model):
	texto = models.CharField(max_length=300, null=False)
	def __str__(self):
		return unicode(self.texto)
	class Meta:
		#ordering = ["texto"]
		verbose_name_plural = "Preguntas"

@python_2_unicode_compatible
class Cuestionario(models.Model):
	grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
	pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
	def __str__(self):
		return unicode(self.grado)+": "+unicode(self.pregunta)
	class Meta:
		ordering = ["grado","pregunta"]
		unique_together = ('grado','pregunta')
		verbose_name_plural = "Cuestionarios"

@python_2_unicode_compatible
class Respuesta(models.Model):
	alumno = models.ForeignKey(Perfil, on_delete=models.CASCADE)
	pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
	texto = models.TextField(max_length=1000, blank=True, null=True)
	def __str__(self):
		return unicode(self.alumno)+" - "+unicode(self.pregunta)+": "+unicode(self.texto)
	class Meta:
		ordering = ["alumno","pregunta"]
		unique_together = ('alumno','pregunta')
		verbose_name_plural = "Respuestas"

class Grupo(models.Model):
	grado = models.ForeignKey(Grado, blank=False, null=False, on_delete=models.CASCADE)
	dn = models.CharField(max_length=200, null=False)
	desc =models.CharField(max_length=300, null=False)
	def __str__(self):
		return str(self.desc)
	class Meta:
		ordering = ["grado","desc"]
		unique_together = ('grado','dn')
		verbose_name_plural = "Grupos"

class Tipo(models.Model):
	clase = models.CharField(max_length=7, null=False, unique=True)
	def __str__(self):
		return str(self.clase)
	class Meta:
		ordering = ["clase"]
		verbose_name_plural = "Tipos"

class Portada(models.Model):
	grado = models.ForeignKey(Grado, blank=False, null=False, on_delete=models.CASCADE)
	tipo = models.ForeignKey(Tipo, blank=False, null=False, on_delete=models.CASCADE)
	mensaje = models.TextField(default=None, blank=True, null=True)
	visible = models.BooleanField(default=False)
	def __str__(self):
		return str(self.grado) + ": " + str(self.mensaje) + " (" + str(self.tipo) + ")"
	class Meta:
		ordering = ["grado"]
		verbose_name_plural = "Portadas"

class Mensaje(models.Model):
	cod = models.CharField(max_length=10, unique=True)
	asunto = models.CharField(max_length=100, null=False)
	cuerpo = models.TextField(default=None, null=False)
	def __str__(self):
		return str(self.cod)
	class Meta:
		ordering = ["cod"]
		verbose_name_plural = "Mensajes"

class Configuracion(models.Model):
	clave = models.CharField(max_length=100, unique=True)
	info = models.TextField(default=None, blank=True, null=True)
	valor = models.BooleanField(default=False)
	def __str__(self):
		return str(self.clave)
	class Meta:
		ordering = ["clave"]
		verbose_name_plural = "Configuraciones"
