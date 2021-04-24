from django.contrib import admin
from .models import Queue, QRCode

admin.site.register(Queue)
admin.site.register(QRCode)