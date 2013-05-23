from sis.core.models import School

def create_school(name, domain):
    _s, _created=School.objects.get_or_create(name=name, domain=domain)


create_school('Test School 1', 'test1.learning42.com')
create_school('Test School 2', 'test2.learning42.com')
create_school('Test School 3', 'test3.learning42.com')