
from django.http import  HttpResponseRedirect#, HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from sis.core.forms import *
from sis.core.util import *
from sis.core.views_parent import get_children

#from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib import messages


@login_required
def home(request):
    #if request.user.is_anonymous():
    #    return HttpResponseRedirect('/accounts/login/?next=/')

    request.session.set_expiry(0)
    try:
        family = request.user.get_profile()
    except:
        return HttpResponseRedirect('/familyinfo')
    if 'view' in request.session:
        view = request.session['view']
    else:
        if family.is_admin():
            view = request.session['view'] = 'admin'
        elif family.is_teacher():
            view = request.session['view'] = 'teacher'
        else:
            view = request.session['view'] = 'parent'

    students = get_children(request)
    teaches = request.user.get_profile().teaches(request)
    
    messages.add_message(request, messages.ERROR, 'Hello world.')
    messages.success(request, 'VIEW:'+view, fail_silently=False)
    print dir(messages)
    print 'get_messages', [m for m in messages.get_messages(request)]
    print 'messages',messages

    if view == 'parent':
        for student in students:
            semester=current_record_semester(request)
            Classes = student.enroll.filter(semester=semester)
            student.assign_categories=[]
            for cl in Classes:
                student.assign_categories+=GradingCategory.objects.filter(classPtr=cl, hasAssignment=True)
        return render_to_response('parent_home.html', locals())
    elif view == 'teacher':
        return render_to_response('teacher_home.html', locals())
    elif view == 'admin':
        return render_to_response('admin_home.html', locals())


@login_required
def change_view(request, view):
    request.session['view'] = view
    return home(request)
    #return HttpResponseRedirect('/')







