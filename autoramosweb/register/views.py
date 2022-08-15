from django.shortcuts import render
from .forms import SignUpForm
from django.urls import reverse
from django.http import HttpResponseRedirect

# Create your views here.
def register(response):
    if response.method == 'POST':
        form = SignUpForm(response.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('login'))
    else:
        form = SignUpForm()
    return render(response, 'register/register.html', {'form': form})
