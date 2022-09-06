from nova_framework.templator import render
from patterns.сreational_patterns import Engine
site = Engine()


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html')


class Contacts:
    def __call__(self, request):
        return '200 OK', render('contacts.html')


class NotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


class CreateCategory:
    def __call__(self, request):

        if request['method'] == 'POST':
            # метод пост
            print(request)
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)

            return '200 OK', render('category_list.html', objects_list=site.categories)
        else:
            categories = site.categories
            return '200 OK', render('create_category.html', categories=categories)


        
class WebinarList:
    def __call__(self, request):
        try:
            category = site.find_category_by_id(int(request['request_params']['id']))
            print (category)
            return '200 OK', render('webinar_list.html', objects_list=category.webinars, name=category.name, id=category.id)
        except KeyError:
            return '200 OK'

class CreateWebinar:
    category_id = -1

    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                webinar = site.create_webinar('record', name, category)
                site.webinars.append(webinar)

            return '200 OK', render('webinar_list.html', objects_list=category.webinars,
                                    name=category.name, id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('create_webinar.html', name=category.name, id=category.id)
            except KeyError:
                return '200 OK'

class CopyWebinar:
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']
            self.category_id = int(request['request_params']['id'])
            category = site.find_category_by_id(int(request['request_params']['id']))
            old_webinar = site.get_webinar(name)
            if old_webinar:
                new_name = f'copy_{name}'
                new_webinar = old_webinar.clone()
                new_webinar.name = new_name
                site.webinars.append(new_webinar)
            web_list =[]
            for web in site.webinars:
                print (web.category.id)
                if int(request['request_params']['id']) == web.category.id:
                    web_list.append(web)
            return '200 OK', render('webinar_list.html', objects_list=web_list,name=category.name, id=category.id)
        except KeyError:
            return '200 OK'

class CategoryList:
    def __call__(self, request):
        return '200 OK', render('category_list.html', objects_list=site.categories)