from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('reserva/', views.reserva_ramos, name='reserva_ramos'),
    path('editar/', views.editar_planner, name='editar_planner'),
    path('equipo/', views.equipo, name='equipo'),
    path('faq/', views.faq, name="faq"),
    path('about/', views.about, name="about"),
    path('reserva/confirmacion/', views.class_log, name="class_log"),
    path('relogin/', views.relogin, name="relogin"),

]
