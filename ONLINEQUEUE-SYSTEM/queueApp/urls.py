from django.urls import path
from . import views


urlpatterns = [
    path('client/<str:pk>', views.client, name='client'),
    path('token/<str:pk>', views.token, name='token'),
    path('staff/', views.staff, name='staff'),
    path('nextone/<str:uuid>', views.nextone, name='nextone'),
    path('delete_qr/<str:uuid>', views.delete_qr, name='del_qr'),
    path('reset_queue/<str:uuid>', views.reset_queue, name='reset_q'),
    
   
]