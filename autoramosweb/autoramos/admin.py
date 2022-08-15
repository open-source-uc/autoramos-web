from django.contrib import admin
from .models import Planner, Cookies

class PlannerAdmin(admin.ModelAdmin):
    list_display = ('user', 'nrc1', 'nrc2', 'nrc3', 'nrc4', 'nrc5', 'nrc6', 'hora_agendada')
    search_fields = ['user']

admin.site.register(Planner, PlannerAdmin)

class CookiesAdmin(admin.ModelAdmin):
    list_display = ('user', 'cookie_value')

admin.site.register(Cookies, CookiesAdmin)
