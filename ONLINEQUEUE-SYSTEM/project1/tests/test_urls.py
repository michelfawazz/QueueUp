from django.test import SimpleTestCase
from django.urls import reverse, resolve
from queuer.views import home
from queueApp.views import *


class TestUrls(SimpleTestCase):

    #urls for queuer 
    def test_home_url_resolved(self):
        url = reverse('Queuer-home')
        print(resolve(url))
        self.assertEquals(resolve(url).func, home)

    #urls for QueueApp
    def test_staff_url_resolved(self):
        url = reverse('staff')
        print(resolve(url))
        self.assertEquals(resolve(url).func, staff)

    def test_client_url_resolved(self):
        url = reverse('client',args=['some-pk'])
        print(resolve(url))
        self.assertEquals(resolve(url).func, client)

    def test_token_url_resolved(self):
        url = reverse('token',args=['some-pk'])
        print(resolve(url))
        self.assertEquals(resolve(url).func, token)

    def test_nextone_url_resolved(self):
        url = reverse('nextone',args=['some-uuid'])
        print(resolve(url))
        self.assertEquals(resolve(url).func, nextone)

    def test_delqr_url_resolved(self):
        url = reverse('del_qr',args=['some-uuid'])
        print(resolve(url))
        self.assertEquals(resolve(url).func, delete_qr)

    def test_resetqr_url_resolved(self):
        url = reverse('reset_q',args=['some-uuid'])
        print(resolve(url))
        self.assertEquals(resolve(url).func, reset_queue)



