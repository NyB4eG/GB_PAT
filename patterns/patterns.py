import copy
import quopri
from time import time
from nova_framework.templator import render
import jsonpickle
import sqlite3
import threading


# архитектурный системный паттерн - UnitOfWork
class UnitOfWork:
    """
    Паттерн UNIT OF WORK
    """
    # Работает с конкретным потоком
    current = threading.local()

    def __init__(self):
        self.new_objects = []
        self.dirty_objects = []
        self.removed_objects = []

    def set_mapper_registry(self, MapperRegistry):
        self.MapperRegistry = MapperRegistry

    def register_new(self, obj):
        #self.new_objects.clear()
        self.new_objects.append(obj)

    def register_dirty(self, obj):
        #self.dirty_objects.clear()
        self.dirty_objects.append(obj)

    def register_removed(self, obj):
        #self.removed_objects.clear()
        self.removed_objects.append(obj)

    def commit(self):
        self.insert_new()
        self.update_dirty()
        self.delete_removed()

        self.new_objects.clear()
        self.dirty_objects.clear()
        self.removed_objects.clear()

    def insert_new(self):
        print(self.new_objects)
        for obj in self.new_objects:
            print(f"Вывожу {self.MapperRegistry}")
            self.MapperRegistry.get_mapper(obj).insert(obj)

    def update_dirty(self):
        for obj in self.dirty_objects:
            self.MapperRegistry.get_mapper(obj).update(obj)

    def delete_removed(self):
        for obj in self.removed_objects:
            self.MapperRegistry.get_mapper(obj).delete(obj)

    @staticmethod
    def new_current():
        __class__.set_current(UnitOfWork())

    @classmethod
    def set_current(cls, unit_of_work):
        cls.current.unit_of_work = unit_of_work

    @classmethod
    def get_current(cls,):
        return cls.current.unit_of_work

class ConsoleWriter:

    def write(self, text):
        print(text)

class DomainObject:

    def mark_new(self):
        UnitOfWork.get_current().register_new(self)

    def mark_dirty(self):
        UnitOfWork.get_current().register_dirty(self)

    def mark_removed(self):
        UnitOfWork.get_current().register_removed(self)

class User:
    def __init__(self, name):
        self.name = name
class Teacher(User):
    pass


class Student(User,DomainObject):

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

    def __init__(self, name, writer=ConsoleWriter()):
        self.name = name
        self.writer = writer

    @staticmethod
    def log(self,text):
        text = f'log---> {text}'
        self.writer.write(text)

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

class StudentMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'student'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name = item
            student = Student(name)
            student.id = id
            result.append(student)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Student(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"
        # Где взять obj.id? Добавить в DomainModel? Или добавить когда берем объект из базы
        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


connection = sqlite3.connect('patterns.sqlite')


# архитектурный системный паттерн - Data Mapper
class MapperRegistry:
    mappers = {
        'student': StudentMapper,
        #'category': CategoryMapper
    }

    @staticmethod
    def get_mapper(obj):

        if isinstance(obj, Student):

            return StudentMapper(connection)
        #if isinstance(obj, Category):
            #return CategoryMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')

class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')