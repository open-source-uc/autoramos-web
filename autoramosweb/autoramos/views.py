from django.shortcuts import render, redirect
from .forms import ScheduleTaskForm, ReLogin
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .backend import verificar_sesion
from django.contrib.auth.decorators import login_required
from .models import Planner, Cookies
import logging
from .tasks import reservar
from datetime import datetime, timedelta
import json
import os

def require_state(required_state: bool, redirect_view_name: str = 'index', required_states: set = {}):
    """Decorador para proteger views por estado de toma"""

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            try:
                planner = Planner.objects.get(user=user)
            except Exception:
                planner = None
            if required_state:
                if planner is None:
                    return redirect(reverse(redirect_view_name))
                
                if planner.estado_toma not in required_states:
                    return redirect(reverse(redirect_view_name))
                else:
                    return view_func(request, *args, **kwargs)
            else:
                if planner is not None:
                    return redirect(reverse(redirect_view_name))
                else:
                    return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


def index(request):
    return render(request, 'autoramos/home.html')

# If not logged in redirect to path specified in
# LOGIN_URL in autoramosweb/settings.py
@login_required()
@require_state(False, redirect_view_name="class_log")
def reserva_ramos(response):
    if response.method == 'POST':
        form = ScheduleTaskForm(response.POST)
        if form.is_valid():
            user = response.user
            
            try:
                planner = Planner.objects.get(user=user)
                planner.nrc1=form.cleaned_data['nrc1']
                planner.nrc2=form.cleaned_data['nrc2']
                planner.nrc3=form.cleaned_data['nrc3']
                planner.nrc4=form.cleaned_data['nrc4']
                planner.nrc5=form.cleaned_data['nrc5']
                planner.nrc6=form.cleaned_data['nrc6']
                planner.estado_toma=1
                
                
            except:
                hora_agendada = datetime.combine(form.cleaned_data['date'], form.cleaned_data['time'])
                planner = Planner.objects.create(user=user, nrc1=form.cleaned_data['nrc1'], nrc2=form.cleaned_data['nrc2'], nrc3=form.cleaned_data['nrc3'], 
                                                 nrc4=form.cleaned_data['nrc4'], nrc5=form.cleaned_data['nrc5'], nrc6=form.cleaned_data['nrc6'],
                                                 estado_toma=1, hora_agendada=hora_agendada)
                
            planner.save()

            complete_datetime = datetime.combine(form.cleaned_data['date'], form.cleaned_data['time'])
            gmt_adjusted = complete_datetime + timedelta(hours=4) # Max culiao genio
            reservar.apply_async(
                args=[response.user.username],
                eta = gmt_adjusted
            )

            #Usar info usuario
            return redirect(reverse('class_log'))

    else:
        form = ScheduleTaskForm()
    return render(response, 'autoramos/reserva.html', {'form': form})

@login_required()
@require_state(True, redirect_view_name="reserva_ramos", required_states={1,4})
def editar_planner(response):
    Planner.objects.get(user=response.user).delete()
    return redirect(reverse('reserva_ramos'))


def equipo(response):
    f = open(os.path.join("static", "assets", "data", "team.json"), 'r', encoding="utf8")
    data = json.load(f)
    f.close()

    return render(response, 'autoramos/equipo.html', {
        "equipo": data
    })

def faq(response):
    f = open(os.path.join("static", "assets", "data", "faq.json"), 'r', encoding="utf8")
    data = json.load(f)
    f.close()

    return render(response, 'autoramos/faq.html', {
        'faq': data
    })

def about(response):
    return render(response, 'autoramos/about.html')

@login_required
@require_state(True, redirect_view_name="reserva_ramos", required_states={1, 2, 3, 4})
def class_log(response):
    if response.method=='POST':
        usuario = response.user
        data = Planner.objects.filter(user=usuario).values('estado_toma', 'nrc1', 'nrc2','nrc3', 'nrc4', 'nrc5', 'nrc6','hora_agendada').first()
        data['hora_agendada'] = (data['hora_agendada'] - timedelta(hours=4)).strftime("%d/%m/%Y a las %H:%M hrs")
        data = {"data": data}
        
        return JsonResponse(data)
    else:
        # Data: Sea igual al enum que le mandemos (1 al 4)
        # 1: Reservados | 2: Tomando | 3: Listo | 4: Error
        return render(response, 'autoramos/log.html') 

@login_required
def relogin(response):
    if response.method == 'POST':
        form = ReLogin(response.POST)
        if form.is_valid():
            test = verificar_sesion(response.user.username, form.cleaned_data['password'])
            if test:
                cookie = Cookies.objects.get(user=response.user.username)
                cookie.estado = True
                cookie.save()
                return HttpResponseRedirect(reverse('reserva_ramos'))
            else:
                form = ReLogin()
                return render(response, 'autoramos/relogin.html', {'form': form})
    else:
        form = ReLogin()
    return render(response, 'autoramos/relogin.html', {'form': form})

