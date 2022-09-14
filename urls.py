from datetime import date
#from views import Index, Contacts, CreateCategory, WebinarList, CreateWebinar, CopyWebinar, CategoryList


# front controller
def secret_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]

# routes = {
#     '/': Index(),
#     '/contacts/': Contacts(),
#     '/create-category/': CreateCategory(),
#     '/webinar-list/': WebinarList(),
#     '/create-webinar/': CreateWebinar(),
#     '/copy-webinar/': CopyWebinar(),
#     '/category-list/': CategoryList()
    
# }