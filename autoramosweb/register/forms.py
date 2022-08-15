import os
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from autoramos.backend import verificar_sesion


def read_csv(path, column):
    with open(path, 'r', encoding='utf-8') as f:
        reader = (line.split(',') for line in f.readlines())
        for line in reader:
            yield line[column]

class SignUpForm(UserCreationForm):
    email = forms.EmailField()

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password1']

        if not verificar_sesion(username, password):
            self.add_error('username', 'Credenciales invalidas (Recuerda ingresar tus credenciales UC)')
            self.add_error('password1', 'Credenciales invalidas (Recuerda ingresar tus credenciales UC)')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            self.add_error('username', 'Ya existe un usuario con ese nombre')
        return username
    
    """Whitelist"""
    # def clean_email(self):
    #     mail = self.cleaned_data['email']
    #     whitelist = read_csv(os.path.join('static', 'assets', 'data', 'reserva.csv'), 1)

    #     if mail not in whitelist:
    #         self.add_error('email', 'No estas en la lista de reservas | Utiliza el correo que ingresaste al reservar cupo.')
    #     return mail

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
