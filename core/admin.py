from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from core.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    '''Создаёт админку '''
    list_display = ('username', 'email', 'first_name', 'last_name')     # поля которые видим
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    # собственные разграничения по полям в админке
    fieldset = (
        (None,
         {'fields': ('username', 'password')}
         ),
        ('Personal info',
         {'fields': ('first_name', 'last_name', 'email')}
         ),
        ('Permissions info',
         {'fields': ('is_active', 'is_staff', 'is_superuser')}
         ),
        ('Other info',
         {'fields': ('last_login', 'date_joined')}
         ),
    )


admin.site.unregister(Group)        # скрываем Группы в админке
