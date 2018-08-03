import unittest
from django.test import Client, TestCase
from django.urls import reverse, resolve
from aliments_manager.forms import ContactForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_urls(self):
        urls = [('/', 'home'), ('/results/steak/1/', 'results'), ('/registration/', 'registration'),\
                ('/connection/', 'connection'), ('/disconnection/', 'disconnection'), ('/account/', 'account'),\
                ('/add_favorite/', 'add_favorite'), ('/favorites/1/', 'favorites'), ('/aliment/1234567891011/', 'aliment'),\
                ('/legalmentions/', 'legalmentions')]
        for url in urls:
            resolver = resolve(url[0])
            self.assertEqual(resolver.url_name, url[1])

    def test_home_form_valid(self):
        form = ContactForm(data={"sujet":"steak"})
        self.assertTrue(form.is_valid())

    def test_home_form_invalid(self):
        form = ContactForm(data={"sujet":"dsfjnsdofdsfoisdfkosdifjosidjfosdifjosdijfosdifjosdifjosdijfoisdjfosdfoisdfjdsfsdfsdoifdsj"})
        self.assertFalse(form.is_valid())

    def test_home_view_redirect(self):
        response = self.client.post(reverse("home"), {"sujet":"steak"}, follow=True)
        print(response.request, response.redirect_chain, response.status_code, "home view redirect")
        self.assertRedirects(response, "/results/steak/1/")

    def test_home_view_return(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aliments_manager/index.html')

    def test_results_view_redirect(self):
        response = self.client.post(reverse("results", kwargs={"aliment_searched":"steak", "page_id":"1"}), {"sujet":"lait"}, follow=True)
        self.assertRedirects(response, "/results/lait/1/")

    def test_registration_view_return(self):
        url = reverse("registration")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aliments_manager/registration.html')

    def test_registration_userNotExisting(self):
        url = reverse("registration")
        response = self.client.post(url, {"nameUser":"rayane", "password":"1234", "email":"rayane@gmail.com"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/connection/')

    def test_registration_userAlreadyExist(self):
        url = reverse("registration")
        rayane = User.objects.create_user(username="rayane", password="1234", email="rayane@gmail.com")
        response = self.client.post(url, {"nameUser":"rayane", "password":"1234", "email":"rayane@gmail.com"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aliments_manager/registration.html')
        
        
    def test_registration_view_redirect(self):
        response = self.client.post(reverse("registration"), {"sujet":"steak"}, follow=True)
        self.assertRedirects(response, "/results/steak/1/")

    def test_change_password_return(self):
        rayane = User.objects.create_user(username="rayane", password="1234")
        url = reverse("change_password")
        logged_in = self.client.login(username='rayane', password='1234')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aliments_manager/change_password.html')

    def test_change_password_redirect(self):
        url = reverse("change_password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_change_password_succeed(self):
        rayane = User.objects.create_user(username="rayane", password="1234")
        url = reverse("change_password")
        logged_in = self.client.login(username='rayane', password='1234')
        response = self.client.post(url, {"actualPassword":"1234", "newPassword":"12345", "confirmNew":"12345"})
        self.assertRedirects(response, "/password_changed")

    def test_change_password_wrong_password(self):
        rayane = User.objects.create_user(username="rayane", password="1234")
        url = reverse("change_password")
        logged_in = self.client.login(username='rayane', password='1234')
        response = self.client.post(url, {"actualPassword":"12345", "newPassword":"12345", "confirmNew":"12345"})
        self.assertTemplateUsed(response, 'aliments_manager/change_password.html')
        
    def test_change_password_wrong_confirmation(self):
        rayane = User.objects.create_user(username="rayane", password="1234")
        url = reverse("change_password")
        logged_in = self.client.login(username='rayane', password='1234')
        response = self.client.post(url, {"actualPassword":"1234", "newPassword":"123456", "confirmNew":"12345"})
        self.assertTemplateUsed(response, 'aliments_manager/change_password.html')

    def test_conncetion_view_return(self):
        url = reverse("connection")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aliments_manager/connection.html')
    
    def test_connection_view_redirect(self):
        response = self.client.post(reverse("connection"), {"sujet":"steak"}, follow=True)
        self.assertRedirects(response, "/results/steak/1/")

    def test_connection_succeed(self):
        url = reverse("connection")
        rayane = User.objects.create_user(username="rayane", password="1234", email="rayane@gmail.com")
        response = self.client.post(url, {"nameUser":"rayane", "password":"1234"})
        self.assertRedirects(response, "/")

    def test_connection_fail(self):
        url = reverse("connection")
        rayane = User.objects.create_user(username="rayane", password="1234", email="rayane@gmail.com")
        response = self.client.post(url, {"nameUser":"rayane", "password":"1235"})
        self.assertTemplateUsed(response, "aliments_manager/connection.html")

    def test_disconnection(self):
        url = reverse("disconnection")
        response = self.client.get(url)
        self.assertRedirects(response, "/")

    def test_account_view_redirect(self):
        url = reverse("account")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_account_redirect(self):
        url = reverse("account")
        response = self.client.post(url, {"sujet":"steak"}, follow=True)
        self.assertRedirects(response, "/results/steak/1/")

    def test_account_view_return(self):
        rayane = User.objects.create_user(username="rayane", password="1234")
        logged_in = self.client.login(username='rayane', password='1234')
        url = reverse("account")
        response = self.client.post(url, {"request.user":rayane})
        self.assertTemplateUsed(response, 'aliments_manager/account.html')
    
    def test_favorites_view_redirect(self):
        url = reverse("favorites", kwargs={"page_id":"1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_favorites_redirect(self):
        url = reverse("favorites", kwargs={"page_id":"1"})
        response = self.client.post(url, {"sujet":"steak"}, follow=True)
        self.assertRedirects(response, "/results/steak/1/")

    def test_favorites_userExist(self):
        rayane = User.objects.create_user(username="rayane", password="1234")
        url = reverse("favorites", kwargs={"page_id":"1"})
        logged_in = self.client.login(username='rayane', password='1234')
        response = self.client.post(url)
        self.assertTemplateUsed(response, "aliments_manager/favorites.html")    

    def test_aliments_view_return(self):
        url = reverse("aliment", kwargs={"code":"3259010108078"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aliments_manager/aliment.html')

    def test_aliments_view_redirect(self):
        url = reverse("aliment", kwargs={"code":"3259010108078"})
        response = self.client.post(url, {"sujet":"steak"}, follow=True)
        self.assertRedirects(response, "/results/steak/1/")

    def test_legalmentions_view_return(self):
        url = reverse("legalmentions")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aliments_manager/legalmentions.html')
