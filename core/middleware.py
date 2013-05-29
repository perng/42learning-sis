from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from sis.core.models import School
#from sis.core.views_admin import signup, new_school_info

from sis.core.models import School, Role, Family
from sis.core.views_admin import signup, edit_school_info
from sis.core.views import home 
from django.contrib import admin
from sis.site_config import *
import django



def is_teacher(request):
    return request.user.get_profile().is_teacher(request.session['school'])

class GetSchool(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        return
        #print 'precess_view', view_func, view_args, view_kwargs, request.META
        path=request.META['PATH_INFO'] 
        host = request.META['HTTP_HOST'] 
        
        if path.startswith(u'/admin/'):# admin interface, skip for all cases, auth handled by admin
            print 'admin'
            return None
        return
        print 'precess_view', view_func
        #print request
        
        if  SIGNUP_SITE  in host: # school admin
            #if request.user.is_anonymous and request.method=='GET':
            #    return HttpResponseRedirect('/accounts/login')

            print 'signup'  
            return None
        
        if 'login' in path:
            print 'login'
            return None
        return None
        if request.user.is_anonymous and request.method=='GET':
            print 'anonymous'
            return HttpResponseRedirect('/accounts/login')
        
        if 'school' not in request.session:
            try:
                school=request.session['school']= request.user.school_set.all()[0]
                request.user.role=request.session['role']=Role.objects.get(user=request.user,school=school)
            except:
                if request.user.is_anonymous():
                    return # home(request)
                return edit_school_info(request)
        elif 'role' not in request.session:
                request.user.role=request.session['role']=Role.objects.get(user=request.user,school=school)
        else:
            request.user.role=request.session['role']
        try:
            request.session['is_teacher']= is_teacher(request)
        except:
            request.session['is_teacher']= False
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


