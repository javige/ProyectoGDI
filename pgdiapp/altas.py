#-*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import render, redirect, render_to_response 
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import *

from utiles import *

import time, datetime

# Dar de alta alumnos
@login_required
def alta(request, grado, usuario):
	if request.user.is_staff:
		alumno = alta_efectiva(grado, usuario)
		return render(request, 'pgdiapp/alta.html', { 'alumno': alumno })

def alta_efectiva(grado, usuario):
	alumno = Perfil.objects.get(user__username=usuario)
	l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
	l.start_tls_s()
	l.simple_bind_s(settings.AUTH_LDAP_ROOT_BIND_DN,settings.AUTH_LDAP_ROOT_BIND_PASSWORD)

	if False: #es_exalumno(usuario):
		# Mover desde exalumnos en ldap
		l.rename_s("cn="+usuario+","+settings.LDAP_EXSTUDENTS_BASE, "cn="+usuario, "ou="+grado+","+settings.LDAP_STUDENTS_BASE)
	else:
		# Crear usuario en ldap
		id_number = calcular_id('uidNumber')
		attrs = {}
		attrs['objectclass'] = ['top', 'posixAccount','shadowAccount','inetOrgPerson', 'organizationalPerson', 'systemQuotas', 'dates'] #, 'person','extensibleObject','pgdi']
		attrs['cn'] = str(alumno.user.username)
		attrs['uid'] = str(alumno.user.username)
		attrs['givenName'] = alumno.nombre.encode('utf-8')
		attrs['sn'] = (alumno.apellido1+" "+alumno.apellido2).encode('utf-8')
		#attrs['gecos'] = ("%s,%s,%s" % (alumno.nombre, alumno.apellido1, alumno.apellido2)).encode('utf-8')
		attrs['mail'] = alumno.email.encode('utf-8')
		attrs['homePhone'] = str(alumno.telefono)
		attrs['mobile'] = str(alumno.telefono)
		attrs['fnac'] = str(alumno.fecha_nac).replace('-','')+'000000Z'
		attrs['fpm'] = str(datetime.date.today().year)+'0901000000Z'
		#attrs['dni'] = str(alumno.dni)
		attrs['businessCategory'] = alumno.trabajo
		attrs['departmentNumber'] = grado.encode('utf-8')
		attrs['employeeType'] = 'primero'
		attrs['carLicense'] = str(alumno.dni)
		attrs['postalCode'] = str(alumno.cp)
		attrs['homePostalAddress'] = alumno.direccion.encode('utf-8')
		attrs['l'] = alumno.localidad.encode('utf-8')
		attrs['st'] = alumno.provincia.encode('utf-8')
		#attrs['c'] = alumno.comunidad.encode('utf-8')
		#attrs['co'] = alumno.pais.encode('utf-8')
		attrs['loginShell'] = str(settings.LOGIN_SHELL)
		attrs['homeDirectory'] = str(generar_directorio(usuario,grado))
		attrs['uidNumber'] = str(id_number)
		attrs['gidNumber'] = alumno.grado.gid.encode('utf-8')
		attrs['userPassword'] = alumno.passwd.encode('utf-8')
		attrs['shadowLastChange'] = str(int(time.time()/86400))
		attrs['shadowMin'] = '300'
		attrs['shadowMax'] = '99999'
		attrs['shadowWarning'] = '7'
		attrs['quota'] = "/dev/vdb1:500000,1000000,0,0"

		dn="cn="+usuario+",ou="+grado.lower()+","+settings.LDAP_STUDENTS_BASE
		ldif = modlist.addModlist(attrs)
		print ldif
		l.add_s(dn,ldif)

		# Crear grupo en ldap
		#attrs = {}
		#attrs['objectclass'] = ['posixGroup','top']
		#attrs['gidNumber'] = str(id_number)
		#attrs['memberUid'] = str(alumno.user.username)

		#dn="cn="+usuario+","+settings.LDAP_OS_BASE
		#ldif = modlist.addModlist(attrs)
		#l.add_s(dn,ldif)

	# Agregar a grupos en ldap
	old = {}
	new = {'memberUid':str(alumno.user.username)}

	#dn="cn=alumnos,"+settings.LDAP_ROLES_BASE
	#ldif = modlist.modifyModlist(old,new)
	#l.modify_s(dn,ldif)

	dn="cn="+grado+","+settings.LDAP_GRADES_BASE
	ldif = modlist.modifyModlist(old,new)
	#l.modify_s(dn,ldif)

	#dn="cn=activos,"+settings.LDAP_ROLES_BASE
	#ldif = modlist.modifyModlist(old,new)
	#l.modify_s(dn,ldif)

	for grp in Grupo.objects.filter(grado__cod=grado):
		try:
			dn=grp.dn
			ldif = modlist.modifyModlist(old,new)
			#l.modify_s(dn,ldif)
		except:
			pass

	l.unbind_s()

	# Actualizar perfil temporal
	alumno.validado = True
	alumno.save()
	# Envíar correo de bienvenida
	#construir_correo(alumno,grado,'WELCOME')
	return alumno
