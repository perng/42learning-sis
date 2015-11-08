from sis.core.models import School
from sis.core.views_admin import signup, new_school_info

# Messed up with new Django
class GetSchool(object):
  def process_view(self, request, view_func, view_args, view_kwargs):
    print 'precess_view', view_func
    request.session['school'] = School.objects.all()[0]
    return None
    # signup.learning42 or  */signup
    if 'signup' in request.META['HTTP_HOST'] or 'signup' in request.META[
      'PATH_INFO']:
      print 'signup'
      return None

    if 'school' not in request.session:
      print 'middleware, not found school'
      host = request.META['HTTP_HOST']
      print 'host', host
      try:

        #request.session['school'] = School.objects.get(domain=host)
        request.session['school'] = School.objects.all()[0]
        print 'found school'
        return None
      except:
        print 'school NOT Found'
        return None
    else:
      if request.session['school'] != request.META['HTTP_HOST']:
        del request.session['school']
        #return self.process_view(request, view_func, view_args, view_kwargs)
        return None