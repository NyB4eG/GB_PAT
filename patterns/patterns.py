import copy
import quopri
from time import time


# порождающий паттерн Прототип - Курс
class WebinarPrototype:
    # прототип курсов обучения

    def clone(self):
        return copy.deepcopy(self)


class Webinar(WebinarPrototype):

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.webinars.append(self)


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


# порождающий паттерн Синглтон
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
