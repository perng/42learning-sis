from sis.core.models import School, Role
from sis.core.views_admin import signup, edit_school_info


class GetSchool(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        print 'precess_view', view_func
        if 'school' not in request.session:
            try:
                school=request.session['school']= request.user.school_set.all()[0]
                request.user.role=request.session['role']=Role.objects.get(user=request.user,school=school)
            except:
                pass
        elif 'role' not in request.session:
                request.user.role=request.session['role']=Role.objects.get(user=request.user,school=school)
        else:
            request.user.role=request.session['role']        
        return
        #print request
        
        # signup.learning42 or  */signup
        if 'signup' in request.META['HTTP_HOST'] or 'signup' in request.META['PATH_INFO']:
            print 'signup'
            return signup(request)
#        for s in School.objects.all():
#            print s.domain
#        for k in request.session.keys():
#            print request.session[k]     
        if 'school' not in request.session:
            print 'middleware, not found school'
            host=request.META['HTTP_HOST']
            print 'host', host
            try:
                
                request.session['school']=School.objects.get(domain=host)
                print 'found school'
                return
            except:
                print 'school NOT Found'
                return signup(request)
        else:
            if request.session['school'] != request.META['HTTP_HOST']:
                del request.session['school']
                return self.process_view(request, view_func, view_args, view_kwargs)
        

