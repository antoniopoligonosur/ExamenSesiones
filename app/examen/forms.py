# ============================================================
# Importaciones
# ============================================================

from django import forms
from django.forms import ModelForm
from examen.models import *
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

# ============================================================
# Formulario Registro
# ============================================================

class RegistroUsuarioForm(UserCreationForm):
    roles = (
        (Usuario.INVESTIGADOR, 'Investigador'),
        (Usuario.PACIENTE, 'Paciente'),
    )   

    rol = forms.ChoiceField(choices=roles)
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password1', 'password2','rol')
    
    def clean(self):
        
        #Validamos con el modelo actual
        super().clean()
        
        # Obtener datos
        rol = self.cleaned_data.get('rol')
        edad = self.cleaned_data.get('edad')

        #Comprobamos
        if(rol == '3' and not edad):
            self.add_error("edad", "Debes rellenar el campo edad.")
        
        if(rol == '2' and edad):
            self.add_error("edad", "Solo lo pueden rellenar los pacientes.")

        #Siempre devolvemos el conjunto de datos.
        return self.cleaned_data

# ============================================================
# Formulario EnsayoClinico (CREAR)
# ============================================================

class EnsayoClinicoForm(ModelForm):

    class Meta:
        model = EnsayoClinico
        fields = [
            "nombre",
            "descripcion",
            "nivel_seguimiento",
            "fecha_inicio",
            "fecha_fin",
            "activo",
            "farmaco",
            "creado_por",
            "pacientes",
        ]

        labels = {
            "nombre": "Titulo",
            "descripcion": "Descripcion",
            "fecha_inicio": "Fecha de Inicio",
            "fecha_fin": "Fecha de Fin",
            "nivel_seguimiento": "Nivel de Seguimiento",
            "activo": "Activo",
            "farmaco": "Farmaco",
            "creado_por": "Creado Por",
            "pacientes": "Pacientes",
        }

        help_texts = {
            "nivel_seguimiento": "Indica el nivel de seguimiento requerido para este ensayo clinico (0-10).",
            "activo": "Indica si el ensayo clinico esta activo o no.",
            "farmaco": "Selecciona el farmaco asociado a este ensayo clinico.",
            "pacientes": "Selecciona los pacientes que participan en este ensayo clinico.",
        }

        widgets = {
            "fecha_inicio": forms.DateTimeInput(attrs={"type": "datetime-local"},format='%Y-%m-%dT%H:%M'),
            "fecha_fin": forms.DateTimeInput(attrs={"type": "datetime-local"},format='%Y-%m-%dT%H:%M'),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):

        super().clean()

        # Obtener datos
        nombre = self.cleaned_data.get('nombre')
        descripcion = self.cleaned_data.get('descripcion')
        farmaco_apto = self.cleaned_data.get('farmaco__apto_para_ensayos')
        nivel_seguimiento = self.cleaned_data.get('nivel_seguimiento')
        edad = self.cleaned_data.get('pacientes__edad')
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        fecha_fin = self.cleaned_data.get('fecha_fin')

        # --- Validaciones personalizadas ---
        # Nombre único, Descripción ≥ 100 caracteres, Fármaco apto, pacientes mayores de edad, nivel de seguimiento 0-10,
        # Fecha inicio < fecha fin, Fecha fin ≥ hoy, Registrar investigador que crea el ensayo desde la sesión (Investigador)
        
        #validacion de nombre unico
        if nombre and EnsayoClinico.objects.filter(nombre=nombre).exists():
            self.add_error("nombre", "El nombre del ensayo clinico ya existe. Debe ser unico.")
            
        #validacion descripcion
        if descripcion and len(descripcion) < 100:
            self.add_error("descripcion", "La descripcion debe tener al menos 100 caracteres.")
            
        #validacion farmaco apto
        if farmaco_apto is False:
            self.add_error("farmaco", "El farmaco seleccionado no es apto para ensayos clinicos.")
        
        #validacion pacientes mayores de edad
        if edad is not None:
            if edad < 18:
                self.add_error("pacientes", "Todos los pacientes deben ser mayores de edad.")
        
        #validacion nivel de seguimiento
        if nivel_seguimiento is not None:
            if nivel_seguimiento < 0 or nivel_seguimiento > 10:
                self.add_error("nivel_seguimiento", "El nivel de seguimiento debe estar entre 0 y 10.")

        #validacion fechas

        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                self.add_error(
                    "fecha_fin",
                    "La fecha de finalización debe ser posterior a la fecha de inicio."
                )
            if fecha_fin < timezone.now().date():
                self.add_error(
                    "fecha_fin",
                    "La fecha de finalización debe ser igual o posterior a la fecha actual."
                )

        return self.cleaned_data
    
# ============================================================
# Formulario Busqueda Avanzada
# ============================================================

# Restricción por usuario logueado: Investigador: solo ve los ensayos que haya creado, Paciente: solo ve ensayos en los que está incluido

class EnsayoClinicoBuscarAvanzada(forms.Form):
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(EnsayoClinicoBuscarAvanzada, self).__init__(*args, **kwargs)
        
        EnsayosClinicosQS = EnsayoClinico.objects
        e_label = "Seleccionar EnsayosClinicos"
        
        if (self.request.user.rol == 1): # Administrador
            EnsayosClinicosQS = EnsayosClinicosQS.all()
            e_label += " (Todos los EnsayosClinicos del Sistema)"
            
        elif (self.request.user.rol == 2): # Investigador
            EnsayosClinicosQS = EnsayosClinicosQS.filter(creado_por__usuario=self.request.user)
            e_label += " (Todos los EnsayosClinicos que ha creado)"
            
        elif (self.request.user.rol == 3): # Paciente
            EnsayosClinicosQS = EnsayosClinicosQS.filter(pacientes__usuario=self.request.user)
            e_label += " (Todos los EnsayosClinicos en los que esta incluido)"
        
        self.fields["EnsayosClinicos"] = forms.ModelMultipleChoiceField(
            label=e_label,
            help_text="(Opcional). Para seleccionar los elementos manten pulsada la tecla Ctrl",
            queryset=EnsayosClinicosQS,
            required=False,
            widget=forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '7'
            })
        )
    
    # Filtros que deben implementar: Que contenga un texto en nombre o descripción, Fecha desde y fecha hasta del inicio del ensayo a la indicada, 
    # Nivel de seguimiento mayo a un valor, Selección múltiple de pacientes, Ensayos activos
    
    texto_contiene = forms.CharField(
        label='Nombre o Descripcion contiene',
        help_text="(Opcional)",
        required=False
    )
    
    fecha_desde = forms.DateField(
        label='Fecha de Inicio desde',
        help_text="(Opcional)",
        required=False,
        widget=forms.DateInput(attrs={'type':'date'})
    )
    
    fecha_hasta = forms.DateField(
        label='Fecha de Inicio hasta',
        help_text="(Opcional)",
        required=False,
        widget=forms.DateInput(attrs={'type':'date'})
    )
    
    nivel_seguimiento_mayor = forms.IntegerField(
        label='Nivel de Seguimiento mayor a',
        help_text="(Opcional)",
        required=False,
        min_value=0,
        max_value=10,
    )
    
    pacientes = forms.ModelMultipleChoiceField(
        label='Seleccionar Pacientes',
        help_text="(Opcional). Para seleccionar los elementos manten pulsada la tecla Ctrl",
        queryset=Paciente.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': '7'
        })
    )
    
    activo = forms.BooleanField(
        label='Solo Ensayos Activos',
        help_text="(Opcional)",
        required=False,
    )
    
    def clean(self):
        
        super().clean()
        
        #Obtenemos los campos
        texto_contiene = self.cleaned_data.get('nombre_contiene')
        fecha_desde = self.cleaned_data.get('fecha_desde')
        fecha_hasta = self.cleaned_data.get('fecha_hasta')
        nivel_seguimiento_mayor = self.cleaned_data.get('nivel_seguimiento_mayor')
        pacientes = self.cleaned_data.get('pacientes')
        activo = self.cleaned_data.get('activo')
        
        #Comprobamos
        
        # Filtros que deben implementar: Que contenga un texto en nombre o descripción:
        
        if (
            texto_contiene == ""
        ):
            self.add_error('texto_contiene','Debes rellenar al menos un campo.')
        if (
            not fecha_desde is None and
            not fecha_hasta is None and
            fecha_hasta < fecha_desde
            ):
            self.add_error('fecha_desde','Rango de fecha no valido.')
            self.add_error('fecha_hasta','Rango de fecha no valido.')
            # Nivel de seguimiento mayor a un valor
        if (
            nivel_seguimiento_mayor is not None and
            nivel_seguimiento_mayor < 0
        ):
            self.add_error('nivel_seguimiento_mayor','El nivel de seguimiento no puede ser negativo.'
        )
            # Selección múltiple de pacientes: 
        if (
            pacientes is not None and
            len(pacientes) == 0
        ):
            self.add_error('pacientes','Debes seleccionar al menos un paciente.')
        if (
            activo is False
        ):
            self.add_error('activo','Debes marcar el campo activo.')
            
        
        
        #Siempre devolvemos el conjunto de datos.
        return self.cleaned_data