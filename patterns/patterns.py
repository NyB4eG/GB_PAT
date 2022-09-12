import copy
import quopri
from time import time
from nova_framework.templator import render
import jsonpickle

class User:
    def __init__(self, name):
        self.name = name
class Teacher(User):
    pass


class Student(User):

    def __init__(self, name):
        self.webinars = []
        super().__init__(name)

class Subject:

    def __init__(self):
        self.observers = []

    def notify(self):
        for item in self.observers:
            item.update(self)

# порождающий паттерн Прототип - Курс
class WebinarPrototype:
    # прототип курсов обучения

    def clone(self):
        return copy.deepcopy(self)


class Webinar(WebinarPrototype, Subject):

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.webinars.append(self)
        self.students = []
        super().__init__()

    
    def __getitem__(self, item):
        return self.students[item]

    def add_student(self, student: Student):
        self.students.append(student)
        student.webinars.append(self)
        self.notify()

# Интерактивный курс
class InteractiveWebinar(Webinar):
    pass


# Курс в записи
class RecordWebinar(Webinar):
    pass



# Категория
class Category:
    # реестр?
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.webinars = []

    def webinar_count(self):
        result = len(self.webinars)
        if self.category:
            result += self.category.webinar_count()
        return result


# порождающий паттерн Абстрактная фабрика - фабрика курсов
class WebinarFactory:
    types = {
        'interactive': InteractiveWebinar,
        'record': RecordWebinar
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, category):
        return cls.types[type_](name, category)

class UserFactory:
    types = {
        'student': Student,
        'teacher': Teacher
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name):
        return cls.types[type_](name)

# Основной интерфейс проекта
class Engine:
    def __init__(self):
        self.teachers = []
        self.students = []
        self.webinars = []
        self.categories = []

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_webinar(type_, name, category):
        return WebinarFactory.create(type_, name, category)

    def get_webinar(self, name):
        for item in self.webinars:
            if item.name == name:
                return item
        return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = quopri.decodestring(val_b)
        return val_decode_str.decode('UTF-8')

    @staticmethod
    def create_user(type_, name):
        return UserFactory.create(type_, name)

    def get_student(self, name) -> Student:
        for item in self.students:
            if item.name == name:
                return item

class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('log--->', text)

class AppRoute:
    def __init__(self, routes, url):
        self.routes = routes
        self.url = url

    def __call__(self, cls):
        self.routes[self.url] = cls()


class Debug:

    def __init__(self, name):

        self.name = name

    def __call__(self, cls):
        def timeit(method):
            def timed(*args, **kw):
                ts = time()
                result = method(*args, **kw)
                te = time()
                delta = te - ts

                print(f'Функция {self.name} выполнилась за {delta:2.2f} мс')
                return result

            return timed

        return timeit(cls)


class TemplateView:
    template_name = 'template.html'

    def get_context_data(self):
        return {}

    def get_template(self):
        return self.template_name

    def render_template_with_context(self):
        template_name = self.get_template()
        context = self.get_context_data()
        return '200 OK', render(template_name, **context)

    def __call__(self, request):
        return self.render_template_with_context()

class ListView(TemplateView):
    queryset = []
    template_name = 'list.html'
    context_object_name = 'objects_list'

    def get_queryset(self):
        print(self.queryset)
        return self.queryset

    def get_context_object_name(self):
        return self.context_object_name

    def get_context_data(self):
        queryset = self.get_queryset()
        context_object_name = self.get_context_object_name()
        context = {context_object_name: queryset}
        return context


class CreateView(TemplateView):
    template_name = 'create.html'

    @staticmethod
    def get_request_data(request):
        return request['data']

    def create_obj(self, data):
        pass

    def __call__(self, request):
        if request['method'] == 'POST':
            data = self.get_request_data(request)
            self.create_obj(data)

            return self.render_template_with_context()
        else:
            return super().__call__(request)

class BaseSerializer:

    def __init__(self, obj):
        self.obj = obj

    def save(self):
        return jsonpickle.dumps(self.obj)

    @staticmethod
    def load(data):
        return jsonpickle.loads(data)   
