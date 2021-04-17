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


#token view to generate a token for clients who scan a qr code each token is linked to a specific qr code instance
def token(request, pk):
    queue_token = Queue.objects.get(pk=pk)
    phone = queue_token.phone_number
    email = queue_token.client_email
    priority = queue_token.priority

    x = queue_token.queue
    y = x - 1

    context = {'token': x,'phone':phone,'after':y,'email':email,'priority':priority}

    return render(request,'queueApp/token.html',context)

# client view this is for the form that the client will have to fill out after he scans the qr code
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

#staff view this is where our users on site can create and manage their queues
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
    unfinished = queue_instances.filter(used=False).order_by('-priority', 'issue_dt')
    unfinishedcount = queue_instances.filter(used=False).count()
    finished = queue_instances.filter(used=True).order_by('-priority', 'issue_dt')
    

    
    if request.method == 'POST' and 'advance' in request.POST:
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


def update_priority(request,uuid, pk):
    
    queue_that_changes = Queue.objects.get(queue=pk)
    if request.method == 'POST' and 'priority' in request.POST:
        queue_that_changes.priority = request.POST['prio']
        queue_that_changes.save()
        messages.success(request, f'priority changed!')
        return redirect('nextone', uuid)

    context = {'queue_that_changes':queue_that_changes }
        
    return render(request, 'queueApp/staff.html', context)


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
    
    if request.method == 'POST' and 'reset' in request.POST:
        queue_instances.delete()
        messages.success(request, f'The Queue And QR Code Has Been Reset!')

        context = {'queue_instances': queue_instances, 'qr': qr_instance, 'unfinished': unfinished, 'finished': finished}
        return render(request, 'queueApp/view_queue.html', context)