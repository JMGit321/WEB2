from django.contrib import admin
from .models import Causa,Doacao, UserProfile
# Register your models here.
@admin.register(Doacao)
class doacaoAdmin(admin.ModelAdmin):
    list_display = ['id','usuario','causa','horario','data']

@admin.register(Causa)
class causeAdmin(admin.ModelAdmin):
    list_display = ['id','usuario','titulo' ,'data',  'foto','recebido','meta',]

admin.site.register(UserProfile)
