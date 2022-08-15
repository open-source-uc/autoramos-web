from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Submit

class ScheduleTaskForm(forms.Form):
    date = forms.DateField(input_formats=['%d/%m/%Y'])
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), help_text='En Formato 24hrs')
    nrc1 = forms.CharField(max_length=5, help_text='Ramo 1', required=True)
    nrc2 = forms.CharField(max_length=5, help_text='Ramo 2', required=False)
    nrc3 = forms.CharField(max_length=5, help_text='Ramo 3', required=False)
    nrc4 = forms.CharField(max_length=5, help_text='Reemplazo ramo 1', required=False)
    nrc5 = forms.CharField(max_length=5, help_text='Reemplazo ramo 2', required=False)
    nrc6 = forms.CharField(max_length=5, help_text='Reemplazo ramo 3', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Column('date'),
                Column('time'),
                css_class = 'row'
            ),
            HTML("<br>"),
            Row(
                Column('nrc1'),
                Column('nrc4'), 
                css_class = 'row'
            ),
            Row(
                Column('nrc2'),
                Column('nrc5'),
                css_class = 'row'
            ),
            Row(
                Column('nrc3'),
                Column('nrc6'),
                css_class = 'row'
            )
        )
        self.helper.add_input(Submit('submit', 'Reservar Toma de Ramos', css_class = 'btn btn-success'))

class ReLogin(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
