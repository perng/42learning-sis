
import datetime, copy
from django.template.loader import get_template
from django.template import *
from django.core import serializers
from django.template import Template
from django.template.defaultfilters import floatformat
from django.views.generic import TemplateView

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin import widgets
import pprint

from sis.core.models import *
from sis.core.forms import *
from sis.core.util import *
from sis.core.views_parent import cal_tuition

from django.contrib.auth import REDIRECT_FIELD_NAME
def superuser_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in and is superuser, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator



@superuser_required
def edit_semester(request, sem_id=0):
    sem = Semester.objects.get(id=id_decode(sem_id)) if sem_id else None
    if not sem:
        sem=Semester(school=request.school)
    if request.method == 'POST':
        sform = SemesterForm(request.POST, instance=sem)
        #sem.school=request.school
        if sform.is_valid():
            sform.save()
            messages.info(request, 'Semester updated')
            return HttpResponseRedirect('/semesterlist')
        else:
            messages.error(request, 'form not valid')
            print  'form not valid', dir(sform)
    else:
        sform = SemesterForm(instance=sem)
    return my_render_to_response(request, 'editsemester.html', locals())

@superuser_required
def semesterlist(request):
    semesters = list(Semester.objects.order_by('-id')[:])

    return my_render_to_response(request, 'semesterlist.html', locals())

def semesters(request):
    semesters = list(Semester.objects.all()[:])
    semesters.sort(key=id)
    if request.method == 'GET':
        sem = semesters[-1] if semesters else None
        if sem:
            classes = Class.objects.filter(semester=sem)
            sform = SemesterForm(instance=sem)
        else:
            sform = SemesterForm()

        return my_render_to_response(request, 'semesters.html', locals())

    sform = SemesterForm(request.POST)
    if sform.is_valid():
        sform.save()
    else:
        print 'form not valid'
    return my_render_to_response(request, 'semesters.html', locals())


@superuser_required
def classlist(request, sem_id):
    sem = Semester.objects.get(id=id_decode(sem_id), school=request.school)
    classes = Class.objects.filter(semester=sem).order_by( "elective","name")
    feeconfig, created = FeeConfig.objects.get_or_create(semester=sem)
    errors=[]
    if request.method == 'POST' and 'feeupdate' in request.POST:
        fees = {}
        for kk in request.POST:
            value = request.POST[kk]
            try:
                key, fid = tuple(kk.split('_'))
                if key not in ['basecc', 'basechk', 'book', 'material', 'misc', 'mdiscount']:
                    continue
                fid = id_decode(fid)
                if fid in fees:
                    fee = fees[fid]
                else:
                    fees[fid] = fee = Fee.objects.get(id=fid)
                try:
                    fvalue = float(value)
                except:
                    errors.append[value + ' is not numerical']
                    continue
                fee.__dict__[key] = fvalue
            except:
                pass
        for fee in fees.values():
            fee.save()
    elif request.method == 'POST' and 'feeconfigupdate' in request.POST:
        feeconfigform = FeeConfigForm(request.POST, instance=feeconfig)
        feeconfigform.fields['semester'].prepare_value(semester)
        if feeconfigform.is_valid():
            feeconfigform.save()
        else:
            print 'feeconfigform is not valid'
            for f in feeconfigform:
                print f
                for e in f.errors:
                    print e

    fee_dict = {}
    for c in classes:
        c.fee, created = Fee.objects.get_or_create(classPtr=c)
        if created:
            c.fee.save()
        fee_dict[str(c.fee.id)] = c.fee
        c.form = ClassFeeForm(instance=c.fee)
    feeconfig, created = FeeConfig.objects.get_or_create(semester=sem)
    if created:
        feeconfig.save()
    feeconfigform = FeeConfigForm(instance=feeconfig)
    return my_render_to_response(request, 'classlist.html', locals())

def create_default_grading_categories(theclass):
    order = 1
    for name, weight, assignment in [('Quiz', 30, False), ('Exam', 40, False), ('Home Work', 30, True), ('Other', 0, False)]:
        #gc,created = GradingCategory.objects.get_or_create(classPtr=theclass, name=name )
        gcs = GradingCategory.objects.filter(classPtr=theclass, name=name )
        if len(gcs)>0:
            gc=gcs[0]
            for g in gcs[1:]:
                g.delete()
        else:
            gc=GradingCategory(classPtr=theclass, name=name, order=order )        
        gc.order=order
        gc.weight=weight
        gc.hasAssignment=assignment
        gc.save()
        order += 1



@superuser_required
def semester(request, sid):
    # 3 possible invokes --- simple get, add class, edit class

    try:
        sem = Semester.objects.get(id=id_decode(sid))
    except:
        print "can't find semester"
        return HttpResponseRedirect('/semesters')

    if request.method == 'GET':
        if sem:
            form = ClassForm()
        else:
            return HttpResponseRedirect('/semesters')
    elif 'addclass' in request.POST:
        print 'addclass'
        form = ClassForm(request.POST)
        if form.is_valid():
            new_class = form.save()
            create_default_grading_categories(new_class)
        else:
            print 'form not valid'
            print 'non-field', form.non_field_errors()
            for f in form:
                print f.name, f.errors

    classes = Class.objects.filter(semester=sem)
    return my_render_to_response(request, 'semester.html', locals())


@superuser_required
def edit_class(request, class_id=0):
    print 'class_id', class_id

    if class_id:
        theclass = Class.objects.get(id=id_decode(class_id))
    if request.method == 'POST':
        if class_id:
            theclass = Class.objects.get(id=int(class_id))
            form = ClassForm(request.POST  , instance=theclass)
        else:
            form = ClassForm(request.POST)
        print 'post'
        if form.is_valid():
            print 'is_valid'
            new_class = form.save()
            create_default_grading_categories(new_class)
            return HttpResponseRedirect('/classlist/%s' % (new_class.semester.eid(),))
    else:
        if class_id:
            form = ClassForm(instance=theclass)
        else:
            form = ClassForm()

    return my_render_to_response(request,'edit_class.html', locals())

@login_required
def sisadmin(request):
    users = User.objects.all()
    if request.method == 'POST':
        post=request.POST
        try:
            staffs = [int(u) for u in post.getlist('staff')]
        except:
            staffs = []
        try:
            admins = [int(u) for u in post.getlist('superuser')]
        except:
            admins = []
        print '--', staffs, admins
        for u in users:
            is_staff, is_superuser = u.id in staffs, u.id in admins          
            u.is_staff, u.is_superuser = is_staff , is_superuser
            u.save()
    return my_render_to_response(request, 'sisadmin.html', locals())


@superuser_required
def family_tuition(request, fid):
    family = Family.objects.get(id=id_decode(fid))
    semester = current_record_semester(request) # the semester open for registration
    tuition, created = Tuition.objects.get_or_create(family=family, semester=semester)

    c = cal_tuition(family, semester, tuition.pay_credit)
    c['request'] = request
    try:
        tuition.due = c['total']
        c['tuition'] = tuition
    except:
        tuition = None

    return my_render_to_response(request, 'family_tuition.html', c)

@superuser_required
def unpaid_payment(request):
    return payment(request, filter='unpaid')

@superuser_required
def payment(request, filter=None):
    semester = current_record_semester() # the semester open for registration
    if not semester:
        print 'no record semester, use the last one'
        semester = Semester.objects.order_by('-id')[0]
    families = {}
    tuitions = Tuition.objects.filter(semester=semester)[:]
    if filter=='unpaid':
        tuitions =[t for t in tuitions if  t.paid!=t.due]
    for tuition in tuitions:
        family = tuition.family
        families[family.id] = family
        family.tuition = tuition
    #families.families.values()
    #families.sort(key='parent1LastName')
    today = datetime.date.today()
    if request.method == 'POST':
        tuitions = {}
        for k in request.POST:
            kk = k.split('-')
            if len(kk) != 2 or not kk[-1].isdigit():
                continue
            fid = id_decode(kk[1])
            family = families[fid]
            key = kk[0]
            if key == 'fully_paid':
                family.tuition.paid = family.tuition.due
            elif key == 'paid':
                try:
                    family.tuition.paid = float(request.POST[k])
                except:
                    print request.POST[k] + ' is not a number'
            elif key == 'checkno':
                family.tuition.checkno = request.POST[k]
        for f in families.values():
            f.tuition.save()

    return my_render_to_response(request, 'registrar.html', locals())

@superuser_required
def active_directory(request, active_only=True):
    semester = current_reg_semester(request)
    classes = semester.class_set.all()
    print 'classes', classes
    families = {}
    for c in classes:
        eds = EnrollDetail.objects.filter(classPtr=c)
        print 'eds', eds
        for ed in eds:
            try:
                family = families[ed.student.family.id]
            except:
                family = ed.student.family
                families[family.id] = family


            try:
                if ed.student.id in family.students:
                    student = family.students[ed.student.id]
                else:
                    student = ed.student
                    family.students[student.id] = student
            except:
                student = ed.student
                family.students = {student.id: student}

            try:
                student.classes[ed.classPtr.id] = str(ed.classPtr.name)
            except:
                student.classes = {ed.classPtr.id:str(ed.classPtr.name)}

    family_list = families.values()
    for f in family_list:
        f.students = f.students.values()
        f.students.sort()
        f.nstudents = len(f.students)
        for i, s in enumerate(f.students):
            s.sno = i
            s.classes = ','.join(s.classes.values())
    return my_render_to_response(request, 'directory.html', locals())

@superuser_required
def teacher_directory(request):
    teachers = Family.objects.all()
    teachers = [t for t in teachers if t.is_teacher()]
    for t in teachers:
        t.teachclass = ','.join([c.name for c in t.teaches()])
    return my_render_to_response(request, 'teacher_directory.html', locals())


def offered_classes(request):
    sem = current_reg_semester(request)
    classes = Class.objects.filter(semester=sem).order_by( "elective","name")
    if not sem or not classes:
        error=['No Class Information Yet. ']
    return my_render_to_response(request, 'offered_classes.html', locals())
    
@superuser_required
def delete_class(request, class_id):
    theclass=Class.objects.get(id=id_decode(class_id))
    sem_id=theclass.semester.id
    theclass.delete()
    return classlist(request, sem_id)

@superuser_required
def system_config(request):
    
    if request.method== 'POST':
        for key in request.POST:
            x=key.split('-')
            if len(x)!=2:
                continue
            nv, name= tuple(x)
            c=Config.objects.get(name=name)
            if nv=='name':
                c.verbose_name= request.POST[key]
            if nv=='value':
                c.set_value(request.POST[key])
            c.save()
    configs=Config.objects.all()
            
    return my_render_to_response(request, 'sys_config.html', locals())


def school_info(request):
    if request.method == 'POST':
        try:
            form = SchoolForm(request.POST, instance=request.school)
        except:
            new=True
            request.school=School()
            form = SchoolForm(request.POST, instance=request.school)
            
        #sem.school=request.school
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
        else:
            print  'form not valid', dir(form)
    else:
        try:
            form= SchoolForm(instance=request.school)
        except:
            new=True
            request.school=School()
            form = SchoolForm(instance=request.school)

    return my_render_to_response(request, 'school_info.html', locals())

def signup(request):
    return my_render_to_response(request, 'signup.html', locals())
    
