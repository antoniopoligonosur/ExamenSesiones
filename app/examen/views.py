# ============================================================
# region Importaciones
# ============================================================

from django.shortcuts import render, redirect
from examen.models import *
from examen.forms import *

from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.decorators import permission_required

from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib import messages


from django.shortcuts import render
from django.views.defaults import page_not_found

from django.core.exceptions import PermissionDenied
from django.db.models import Q

#---HOME---
def home(request):
    return render(request, 'pages/home.html')

#--- Detalles Usuario ---
def dame_usuario(request, id_usuario):
    
    usuario = (
        Usuario.objects
        .get(id=id_usuario)
    )
    
    return render(request, 'models/usuario/detalles_usuario.html',{'Usuario_Mostrar':usuario})

# --- Lista Usuario ---
def usuarios_listar(request):
    
    usuarios = (
        Usuario.objects
        .all()
    )
    
    return render(request, 'models/usuario/lista_usuario.html',{'Usuarios_Mostrar':usuarios})

#--- Detalles Investigador ---
def dame_investigador(request, id_investigador):
    
    investigador = (
        Investigador.objects
        .select_related('usuario')
        .get(id=id_investigador)
    )
    
    return render(request, 'models/investigador/detalles_investigador.html',{'investigador_Mostrar':investigador})

#--- Lista Investigadores ---
def investigadores_listar(request):
    
    investigadores = (
        Investigador.objects
        .select_related('usuario')
        .all()
    )
    
    return render(request, 'models/investigador/lista_investigador.html',{'investigadores_Mostrar':investigadores})

# --- CREATE ---

@permission_required('examen.add_EnsayoClinico', raise_exception=True)
def EnsayoClinico_create(request):  # Método que controla el tipo de formulario

    # Si la petición es GET se creará el formulario vacío
    # Si la petición es POST se creará el formulario con datos.
    datosFormulario = None

    if request.method == "POST":
        datosFormulario = request.POST

    formulario = EnsayoClinicoForm(datosFormulario)

    if (request.method == "POST"):

        EnsayoClinico_creado = crear_EnsayoClinico_modelo(formulario, request.user)

        if (EnsayoClinico_creado):

            nombre_EnsayoClinico = formulario.cleaned_data.get('nombre')

            messages.success(
                request,
                'Se ha creado el EnsayoClinico: [ ' + nombre_EnsayoClinico + ' ] correctamente.'
            )
            return redirect('EnsayosClinicos_listar')

    return render(
        request,
        'models/EnsayosClinicos/crud/create_EnsayoClinico.html',
        {'formulario': formulario}
    )

def crear_EnsayoClinico_modelo(formulario, usuario):  # Método que interactúa con la base de datos
    
    EnsayoClinico_creado = False

    # Comprueba si el formulario es válido
    if formulario.is_valid():
        try:
            # Guarda el EnsayoClinico en la base de datos
            EnsayoClinico = formulario.save(commit=False)

            # asignar creador SIEMPRE
            EnsayoClinico.investigador = usuario.investigador

            EnsayoClinico.save()
            formulario.save_m2m()  # por el ManyToManyField
            
            EnsayoClinico_creado = True
            
        except Exception as error:
            print(error)

    return EnsayoClinico_creado

#---READ---

@permission_required('examen.view_EnsayoClinico', raise_exception=True)
def EnsayosClinicos_listar(request):
    
    EnsayosClinicos = (
        EnsayoClinico.objects
            .select_related(
                "farmaco",
                "creado_por",
                "creado_por__usuario",
            )
            .all()
    )
    
    return render(request,'models/EnsayosClinicos/crud/lista_EnsayosClinicos.html',{'EnsayosClinicos_Mostrar':EnsayosClinicos})

@permission_required('examen.view_EnsayoClinico', raise_exception=True)
def EnsayosClinicos_buscar_avanzado(request):  # Búsqueda Avanzada para EnsayosClinicos

    if len(request.GET) > 0:
        formulario = EnsayoClinicoBuscarAvanzada(request.GET, request = request)
        if formulario.is_valid():

            mensaje_busqueda = 'Filtros Aplicados:\n'
            QsEnsayoClinico = (
                EnsayoClinico.objects
                .select_related(
                    "farmaco",
                    "creado_por",
                    "creado_por__usuario",
                )
            )
            # Obtener valores del formulario
            texto_contiene = formulario.cleaned_data.get('texto_contiene')
            fecha_desde = formulario.cleaned_data.get('fecha_desde')
            fecha_hasta = formulario.cleaned_data.get('fecha_hasta')

            # --- Texto contiene ---
            if texto_contiene != '':
                texto_contiene = texto_contiene.strip()
                QsEnsayoClinico = QsEnsayoClinico.filter(nombre__icontains=texto_contiene)
                mensaje_busqueda += f'· Nombre contiene "{texto_contiene}"\n'
            else:
                mensaje_busqueda += '· Cualquier nombre\n'

            # --- Fecha desde ---
            if fecha_desde is not None:
                QsEnsayoClinico = QsEnsayoClinico.filter(fecha_inicio__gte=fecha_desde)
                mensaje_busqueda += f'· Desde fecha de inicio: {fecha_desde}\n'
            else:
                mensaje_busqueda += '· Cualquier fecha de inicio\n'

            # --- Fecha hasta ---
            if fecha_hasta is not None:
                QsEnsayoClinico = QsEnsayoClinico.filter(fecha_final__lte=fecha_hasta)
                mensaje_busqueda += f'· Hasta fecha fin: {fecha_hasta}\n'
            else:
                mensaje_busqueda += '· Cualquier fecha de fin\n'

            # Query final
            EnsayosClinicos = QsEnsayoClinico.all()

            return render(
                request,
                'models/EnsayosClinicos/crud/lista_EnsayosClinicos.html',
                {
                    'EnsayosClinicos_Mostrar': EnsayosClinicos,
                    'Mensaje_Busqueda': mensaje_busqueda,
                }
            )
        
    else:
        formulario = EnsayoClinicoBuscarAvanzada(None, request = request)
    return render(
        request,
        'models/EnsayosClinicos/crud/buscar_avanzada_EnsayosClinicos.html',
        {'formulario': formulario}
    )

# ============================================================
# Registro
# ============================================================

def registrar_usuario(request):
    
    if request.user.is_authenticated:
        messages.info(request, 'Debe Cerrar Sesion para poder volver a Registrarse')
        return redirect('home')
    
    if request.method == 'POST':
        formulario = RegistroUsuarioForm(request.POST)
        
        if formulario.is_valid():
            
            rol = int(formulario.cleaned_data.get('rol'))
            
            user = formulario.save(commit=False)
            user.save()
            
            if(rol == Usuario.paciente):
                
                # Agregar el usuario a los grupos
                grupo_usuario = Group.objects.get(name='Paciente')
                grupo_usuario.user_set.add(user)
                
            elif(rol == Usuario.investigador):
                
                # Agregar el usuario a los grupos
                grupo_usuario = Group.objects.get(name='Investigador')
                grupo_usuario.user_set.add(user)
                
                # Crear el Objeto tecnico con la fk del usuario
                investigador = Investigador.objects.create(usuario = user)
                investigador.save()
            
            # Hacer el Login Automatico
            login(request, user)
            
            # 2 Variables en la Sesion
            # control de visibilidad según rol y sesión
            
            request.session['rol'] = user.rol
            
            # Hora Login
            request.session['hora_login'] = timezone.now().strftime("%d/%m/%Y %H:%M")
            
            # Visitas
            if 'contador_visitas' not in request.session:
                request.session['contador_visitas'] = 0
            else:
                request.session['contador_visitas'] += 1
            
            #-------------------------------------------------------------------------------
            
            return redirect('home')
    else:
        formulario = RegistroUsuarioForm()
        
    return render(request, 'registration/signup_usuario.html', {'formulario': formulario})

#---UPDATE---

@permission_required('examen.change_EnsayoClinico', raise_exception=True)
def EnsayoClinico_editar(request, id_ensayoclinico):  # Actualizar EnsayoClinico
    
    # Debe tenerse en cuenta que validaciones no podemos aplicar en el momento de editar.Pista: hay dos casos.
    # Solo puede editar los ensayos el investigador que haya creado el ensayo
    
    ensayoClinico = EnsayoClinico.objects.get(id=id_ensayoclinico)
    
    if request.user.rol == Usuario.INVESTIGADOR:
        # Verificar si el usuario logueado es el dueño del EnsayoClinico
        if ensayoClinico.creado_por.usuario != request.user:
            raise PermissionDenied("No tienes permiso para editar este EnsayoClinico porque no eres el dueño.")
    
    # Si la petición es GET se creará el formulario Vacío
    # Si la petición es POST se creará el formulario con Datos.
    datosFormulario = None
    
    if request.method == "POST":
        datosFormulario = request.POST
    
    formulario = EnsayoClinicoForm(datosFormulario, instance=ensayoClinico)
    
    if (request.method == "POST"):
        
        ensayoClinico_actualizado = crear_EnsayoClinico_modelo(formulario, request.user)
        
        if (ensayoClinico_actualizado):
            
            nombre = formulario.cleaned_data.get('nombre')
            
            messages.success(request, 'Se ha actualizado el EnsayoClinico: [ ' + nombre + " ] correctamente.")
            return redirect('EnsayosClinicos_listar')
    
    return render(request, 'models/EnsayosClinicos/crud/actualizar_EnsayosClinicos.html', {'formulario': formulario, 'EnsayoClinico': ensayoClinico})

#---DELETE---

@permission_required('examen.delete_EnsayoClinico', raise_exception=True)
def EnsayoClinico_eliminar(request, id_ensayoclinico):  # Eliminar EnsayoClinico
    
    # Debe tenerse en cuenta que validaciones no podemos aplicar en el momento de editar.Pista: hay dos casos.
    # Solo puede eliminar los ensayos el investigador que haya creado el ensayo

    if request.user.rol == Usuario.INVESTIGADOR:
        ensayoClinico = EnsayoClinico.objects.get(id=id_ensayoclinico)
        # Verificar si el usuario logueado es el dueño del EnsayoClinico
        if ensayoClinico.creado_por.usuario != request.user:
            raise PermissionDenied("No tienes permiso para eliminar este EnsayoClinico porque no eres el dueño.")

    ensayoClinico = EnsayoClinico.objects.get(id=id_ensayoclinico)
    nombre = EnsayoClinico.nombre
    try:
        EnsayoClinico.delete()
        messages.success(request, 'Se ha eliminado el EnsayoClinico [ ' + nombre + ' ] correctamente.')
    except Exception as error:
        print(error)
    return redirect('EnsayosClinicos_listar')

# ============================================================
# Login
# ============================================================

class MiLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.request.user
        
        # 2 Variables en la Sesion
        
        # Hora Login
        self.request.session['hora_login'] = timezone.now().strftime("%d/%m/%Y %H:%M")
        
        # Visitas
        if 'contador_visitas' not in self.request.session:
            self.request.session['contador_visitas'] = 0
        else:
            self.request.session['contador_visitas'] += 1

        #-------------------------------------------------------------------------------

        return response

# ============================================================
# Errores personalizados (400, 403, 404, 500)
# ============================================================

def mi_error_404(request,exception=None):
    return render(request,'error/404.html',None,None,404)

def mi_error_403(request,exception=None):
    return render(request,'error/403.html',None,None,403)

def mi_error_400(request,exception=None):
    return render(request,'error/400.html',None,None,400)

def mi_error_500(request,exception=None):
    return render(request,'error/500.html',None,None,500)