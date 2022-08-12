import quopri

# Парсим полученный запрос
class ParseData:
    @staticmethod
    def parse_input_data(data: str):
        result = {}
        if data:
            params = data.split('&')
            for item in params:
                k, v = item.split("=")
                result[k] = v
        return result


# Обработка GET запроса
class GetRequests(ParseData):
    @staticmethod
    def get_request_params(environ):
        query_string = environ["QUERY_STRING"]
        request_params = GetRequests.parse_input_data(query_string)
        return request_params


# Обработка POST запроса
class PostRequests(ParseData):
    @staticmethod
    def get_wsgi_input_data(env) -> bytes:
        content_length_data = env.get("CONTENT_LENGTH")
        content_length = int(content_length_data) if content_length_data else 0
        data = env["wsgi.input"].read(content_length) if content_length > 0 else b""
        return data

    def parse_wsgi_input_data(self, data: bytes) -> dict:
        result = {}
        if data:
            data_str = data.decode(encoding="utf-8")
            result = self.parse_input_data(data_str)
        return result

    def get_request_params(self, environ):
        data = self.get_wsgi_input_data(environ)
        data = self.parse_wsgi_input_data(data)
        return data


class PageNotFound404:
    def __call__(self, request):
        return "404 WHAT", "404 PAGE Not Found"


class Framework:

    """Класс Framework - основа фреймворка"""

    def __init__(self, routes_obj, fronts_obj):
        self.routes_lst = routes_obj
        self.fronts_lst = fronts_obj

    def __call__(self, environ, start_response):
        # получаем адрес, по которому выполнен переход
        path = environ["PATH_INFO"]

        # добавление закрывающего слеша
        if not path.endswith("/"):
            path = f"{path}/"

        request = {}
        method = environ["REQUEST_METHOD"]
        request["method"] = method

        # Получения данных запроса
        if method == "POST":
            data = PostRequests().get_request_params(environ)
            request["data"] = data
            print(f"post-запрос: {Framework.decode_value(data)}")
        if method == "GET":
            request_params = GetRequests().get_request_params(environ)
            request["request_params"] = request_params
            print(f"GET-запрос с параметрами: {request_params}")

        # находим нужный контроллер
        # отработка паттерна page controller
        if path in self.routes_lst:
            view = self.routes_lst[path]
        else:
            view = PageNotFound404()
        request = {}
        # наполняем словарь request элементами
        # этот словарь получат все контроллеры
        # отработка паттерна front controller
        for front in self.fronts_lst:
            front(request)
        # запуск контроллера с передачей объекта request
        code, body = view(request)
        start_response(code, [("Content-Type", "text/html")])
        return [body.encode("utf-8")]

    @staticmethod
    def decode_value(data):
        new_data = {}
        for k, v in data.items():
            val = bytes(v.replace("%", "=").replace(" ", " "), "UTF-8")
            val_decode_str = quopri.decodestring(val).decode("UTF-8")
            new_data[k] = val_decode_str
        return new_data
