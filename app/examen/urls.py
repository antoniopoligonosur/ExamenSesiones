# ============================================================
# region Importaciones
# ============================================================

from django.urls import path
from . import views
from .views import MiLoginView

# endregion
# ============================================================


urlpatterns = [
    
    #---HOME---
    path('',views.home, name='home'),
    
    # Registro
    path('registro/usuario',views.registrar_usuario,name='registrar_usuario'),
    
    # Login
    path('accounts/login/', MiLoginView.as_view(), name='login'),

    #---Usuario---
    path('usuario/listar', views.usuarios_listar, name='usuarios_listar'),
    path('usuario/<int:id_usuario>', views.dame_usuario, name='dame_usuario'),
    
    #---investigador---
    path('investigador/listar', views.investigadores_listar, name='investigadore_listar'),
    path('investigador/<int:id_investigador>', views.dame_investigador, name='dame_investigador'),
    
    #---CRUD---
    path('ensayoclinico/crear', views.EnsayoClinico_create, name='EnsayoClinico_crear'),
    path('ensayoclinico/listar', views.EnsayosClinicos_listar, name='EnsayosClinicos_listar'),
    path('ensayoclinico/editar/<int:id_ensayoclinico>', views.EnsayoClinico_editar, name='EnsayoClinico_editar'),
    path('ensayoclinico/eliminar/<int:id_ensayoclinico>', views.EnsayoClinico_eliminar, name='EnsayoClinico_eliminar'),
    
]