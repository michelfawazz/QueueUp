from django.forms import ModelForm
from .models import Queue


class queueForm(ModelForm):
    class Meta:
        model = Queue
        fields = ['client_name','phone_number','client_email']