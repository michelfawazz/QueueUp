from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from uuid import uuid4
from users.models import Profile


class QRCode(models.Model):
    name = models.CharField(max_length=100, null=True)
    uuid = models.UUIDField(blank=True, null=True)
    created_by = models.ForeignKey(Profile, blank=True, null=True, on_delete=models.CASCADE)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        new_id = uuid4()
        # make sure to change this url when website goes live
        qrcode_img = qrcode.make(f'https://queueup253.herokuapp.com/client/{new_id}')
        self.uuid = new_id
        canvas = Image.new('RGB', (500, 500), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        fname = f'QR_{self.name}.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)
        
        
class Queue(models.Model):
    client_name = models.CharField(max_length=20, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    client_email = models.EmailField(null=True)
    priority = models.IntegerField(default=1, null=True)
    queue = models.IntegerField(null=True)
    issue_dt = models.DateTimeField(null=True, auto_now_add=True)
    used = models.BooleanField(null=True, default=False)
    qr_instance = models.ForeignKey(QRCode, blank=True, null=True, on_delete=models.CASCADE)