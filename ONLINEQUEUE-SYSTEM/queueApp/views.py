from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import sys
from django.contrib import messages
from .forms import queueForm
from django.contrib.auth.decorators import login_required
from .models import QRCode, Queue



def token(request, pk):
    queue_token = Queue.objects.get(pk=pk)
    phone = queue_token.phone_number
    email = queue_token.client_email

    x = queue_token.queue
    y = x - 1

    context = {'token': x,'phone':phone,'after':y,'email':email,}

    return render(request,'queueApp/token.html',context)


def client(request, pk):
    form = queueForm()
    qr_instance = QRCode.objects.get(uuid=pk)
    if request.method == 'POST':
        name = request.POST.get('client_name')
        phone = request.POST.get('phone_number')
        email = request.POST.get('client_email')
        number_of_queue_instances = len(qr_instance.queue_set.all()) or 0
        user_has_queue = qr_instance.queue_set.filter(phone_number=phone).first()

        if not user_has_queue:
            queue = Queue(client_name=name,
                          phone_number=phone,
                          client_email=email,
                          queue=(number_of_queue_instances+1),
                          qr_instance=qr_instance)
            queue.save()

            template = render_to_string('queueApp/placedinq_template.html', {'name': name})
            notiemail = EmailMessage(
                'You have been placed in the Queue',
                template,
                settings.EMAIL_HOST_USER,
                [email]
            )
            notiemail.fail_silently=False
            notiemail.send()

            return redirect('token', str(queue.id))
        else:
            return redirect('token', user_has_queue.pk)

    context = {'form': form}
    return render(request, 'queueApp/client.html', context)


@login_required
def staff(request):
    qr_codes = QRCode.objects.filter(created_by=request.user.profile)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        new_generated_code = QRCode(name=name, created_by=request.user.profile)
        new_generated_code.save()
        messages.success(request, f'You have generated a new Queue with its own QR code!')

        return redirect('staff')
        
    context = {'qr_codes': qr_codes}
    return render(request, 'queueApp/staff.html', context)


def nextone(request, uuid):
    qr_instance = QRCode.objects.get(uuid=uuid)
    queue_instances = qr_instance.queue_set.all().order_by('queue')
    unfinished = queue_instances.filter(used=False)
    finished = queue_instances.filter(used=True)

    
    if request.method == 'POST':
        if unfinished.exists():

            queue_that_advances = unfinished.first()
            queue_that_advances.used = True
            queue_that_advances.save()
            # to send an email
            template = render_to_string('queueApp/email_template.html', {'name':queue_that_advances.client_name})
            notiemail = EmailMessage(
                'Its Your Turn Now!',
                template,
                settings.EMAIL_HOST_USER,
                [queue_that_advances.client_email]
            )
            notiemail.fail_silently=False
            notiemail.send()

            return redirect('nextone', uuid)
        else:
            messages.success(request, f'The Queue is Empty!')


    context = {'queue_instances': queue_instances, 'qr': qr_instance, 'unfinished': unfinished, 'finished': finished}
    return render(request, 'queueApp/view_queue.html', context)



def delete_qr(request, uuid):
    qr_instance = QRCode.objects.get(uuid=uuid)

    if request.method == 'POST':
        qr_instance.delete()
        messages.success(request, f'The Queue And QR Code Has Been Deleted!')

        return redirect('staff')


def reset_queue(request, uuid):
    qr_instance = QRCode.objects.get(uuid=uuid)
    queue_instances = qr_instance.queue_set.all().order_by('queue')
    unfinished = queue_instances.filter(used=False)
    finished = queue_instances.filter(used=True)
    
    if request.method == 'POST':
        queue_instances.delete()
        messages.success(request, f'The Queue And QR Code Has Been Reset!')

        context = {'queue_instances': queue_instances, 'qr': qr_instance, 'unfinished': unfinished, 'finished': finished}
        return render(request, 'queueApp/view_queue.html', context)