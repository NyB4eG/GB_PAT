from nova_framework.main import Framework
from urls import routes, fronts
from wsgiref.simple_server import make_server

application = Framework(routes, fronts)

with make_server('', 8001, application) as httpd:
    print("Запуск на порту 8001...")
    httpd.serve_forever()
