# ============================================================
# region Importaciones
# ============================================================

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

# endregion
# ============================================================


# python manage.py migrate          <-- Comando para generar la base de datos
# python manage.py generar_grupos   <-- Comando para generar los grupos y permisos

# python manage.py dumpdata --indent 4 > examen/fixtures/datos.json   <-- Comando para guardar los datos


class Command(BaseCommand):
    help = "Crea los grupos y asigna los permisos necesarios."

    def handle(self, *args, **kwargs):

        # ============================================================
        # region Creacion de Grupos y Permisos
        # ============================================================
        
        self.stdout.write("Creando grupos...")

        # Diccionario con los grupos y sus permisos
        grupos = {
            # ______________________ GRUPO ADMINISTRADOR __________________________
            "Administrador": [
                
                "add_usuario", "change_usuario", "delete_usuario", "view_usuario",
            ],
            # ______________________ GRUPO INVESTIGADOR __________________________
            "Investigador": [
                
                "add_usuario", "change_usuario", "delete_usuario", "view_usuario",
            ],
            # ______________________ GRUPO PACIENTE ________________________________
            "Paciente": [
                
                "view_usuario",
            ],
        }

        for nombre_grupo, permisos in grupos.items():

            grupo, creado = Group.objects.get_or_create(name=nombre_grupo)

            if creado:
                self.stdout.write(f"Grupo creado: {nombre_grupo}")
            else:
                self.stdout.write(f"Grupo ya existia: {nombre_grupo}")

            # Agregar permisos
            for codename in permisos:
                try:
                    permiso = Permission.objects.get(codename=codename)
                    grupo.permissions.add(permiso)
                    
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"Permiso no encontrado: {codename}")
                    )

        self.stdout.write(self.style.SUCCESS("Grupos creados y actualizados correctamente."))
        
        # endregion
        # ============================================================


        # ============================================================
        # region Para ver todos los permisos disponibles por consola
        # ============================================================

        """
        
        self.stdout.write("\nPermisos disponibles en la app:\n")
        
        app_label = "Concursos_Online"
        
        content_types = ContentType.objects.filter(app_label=app_label)
        
        permisos_app = Permission.objects.filter(content_type__in=content_types)
        
        for p in permisos_app:
            self.stdout.write(f"- {p.codename}   ({p.name})")
        
        
        self.stdout.write(self.style.SUCCESS("\nListado completo de permisos mostrado con exito."))
        
        """
        
        # endregion
        # ============================================================