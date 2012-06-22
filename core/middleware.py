from sis.core.models import School
from sis.core.views_admin import signup

class GetSchool(object):
    def process_request(self, request):        
        if 'school' not in request.__dict__:
            print 'middleware, not found school'
            host=request.META['HTTP_HOST'].split(':')[0]
            try:
                request.school=School.objects.get(domain=host)
            except:
                return signup(request)

