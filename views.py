from nova_framework.templator import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html')


class Contacts:
    def __call__(self, request):
        return '200 OK', render('contacts.html')


class NotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'
