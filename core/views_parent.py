
#import datetime, copy
#from django.template.loader import get_template
#from django.template import *
#from django.core import serializers
#from django.template import Template
#from django.template.defaultfilters import floatformat
#from django.views.generic import TemplateView

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
#from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.contrib import messages
from django.contrib.auth.decorators import login_required #, user_passes_test
#from django.contrib.admin import widgets

from sis.core.models import *
from sis.core.forms import *
from sis.core.util import id_decode, lookup, my_render_to_response
from sis.core.views_admin import manage_enrollment

def get_children(request):
    try:
        family = request.user.get_profile()
        return Student.objects.filter(family=family)
    except:
        pass
    return []

def student_access(user, student):
    # if admin, grant access
    if user.is_superuser:
        return True
    # if parent of the student
    try:
        family = user.get_profile()
        return student.family == family   # if student is empty, raise exception here too
        return True
    except:
        pass

    # if user is teacher, teaching the student , to be done
    return False

@login_required
def profile(request):
    try:
        _family = request.user.get_profile()
        return HttpResponseRedirect('/')
    except:
        return HttpResponseRedirect('/familyinfo')

@login_required
def user_profile(request,uid):
    return familyinfo(request)

@login_required
def familyinfo(request):
    if request.method == 'GET':
        try:
            family = request.user.get_profile()
            form = FamilyForm(instance=family)
            students = family.student_set.order_by('-birthday')
        except:
            form = FamilyForm()
        return my_render_to_response(request, 'family.html', locals())

    try:
        family = request.user.get_profile()
        family.cache()
        family.user = request.user
        form = FamilyForm(request.POST, instance=family)
    except:
        family = Family()
        family.user = request.user
        form = FamilyForm(request.POST, instance=family)
    students = family.student_set.order_by('-birthday')
    if form.is_valid():
        form.save()
        messages.info(request, 'Family Information Updated.')
        return HttpResponseRedirect('/')
    else:
        messages.error(request, 'Please fix errors')
        return my_render_to_response(request, 'family.html', locals())

import time
def next_student_id():
    return str(int(time.time()))


@login_required
def edit_student(request, sid=0):
    if sid:
        student = Student.objects.get(id=id_decode(sid))
    else:
        student = Student()
    #if sid and not student_access(request.user, student):
    #    messages.error(request, 'You are not authorized to access information of this student.')
    #    print 'You are not authorized to access information of this student.'
    #    return HttpResponseRedirect('/')
    if request.method == 'GET':
        form = StudentForm(instance=student)
    else: # POST
        if not sid:
            student = Student(studentID=next_student_id(), family=request.user.get_profile())
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.info(request, 'Student information for %s saved. ' % (student.firstName + ' ' + student.lastName,))
            return HttpResponseRedirect('/')
    return my_render_to_response(request, 'edit_student.html', locals())


@login_required
def student_score(request, sid):
    student = Student.objects.get(id=id_decode(sid))
    semester=current_record_semester()
    student.enrolledClasses = student.enroll.filter(semester=semester)
    
    for aclass in student.enrolledClasses:
        aclass.sessions = aclass.classsession_set.order_by('date')
        aclass.show_attendance = aclass.recordAttendance and aclass.sessions
        for cs in aclass.sessions:
            cs.att, create = Attendance.objects.get_or_create(student=student, session=cs)
            aclass.categories = aclass.gradingcategory_set.order_by('order')
            for cat in aclass.categories:
                cat.gds = cat.gradingitem_set.order_by('date')
                for gd in cat.gds:
                    try:
                        gd.score = Score.objects.get(gradingItem=gd, student=student)
                    except:
                        gd.score = '_'
    return my_render_to_response(request, 'student_score.html', locals())


@login_required
def enroll_form(request, family_id,  errors=[]):
    #family = request.user.get_profile()
    family = Family.objects.get(id=id_decode(family_id))

    semester = current_reg_semester()
    error = None
    if not semester:
        enrollment_not_open = True
        return my_render_to_response(request, 'enroll.html', locals())
    #students = get_children(request)
    students = family.get_children()

    print students
    if not students:
        error = 'No student listed under this account'
        return my_render_to_response(request, 'enroll.html', locals())
    mclasses = Class.objects.filter(semester=semester, elective=False)
    eclasses = Class.objects.filter(semester=semester, elective=True)

    for s in students:
        s.mclass = s.eclass = 0
    for c in mclasses:
        for s in students:
            if s in c.student_set.all():
                s.mclass = c.id

    for c in eclasses:
        for s in students:
            if s in c.student_set.all():
                s.eclass = c.id

    return my_render_to_response(request, 'enroll.html', locals())

@login_required
def enroll(request, family_id):
    #family = request.user.get_profile()
    family = Family.objects.get(id=id_decode(family_id))

    semester = current_reg_semester()
    students = family.get_children()
    print request.POST
    mclasses = Class.objects.filter(semester=semester, elective=False)
    eclasses = Class.objects.filter(semester=semester, elective=True)
    for s in students:
        s.eclass = s.mclass = None
        for c in list(mclasses) + list(eclasses):
            # c.student_set.remove(s)
            EnrollDetail.objects.filter(student=s, classPtr=c).delete()


    for k in request.POST:
            v = request.POST[k]
            print k, v
            k = str(k)
            if  'class' not in k or v == '---':
                continue
            cid = id_decode(v)
            theClass = Class.objects.get(id=cid)
            sid = id_decode(k.split('-')[1])
            student = lookup(sid, students)
            if k.startswith('classm'):
                    if s.mclass:
                        oldm = Class.objects.get(id=s.mclass.id)
                        #oldm.student_set.remove(student)
                        EnrollDetail.objects.filter(classPtr=oldm, student=student).delete()
                    #theClass.student_set.add(student)
                    ed = EnrollDetail(student=student, classPtr=theClass)
                    ed.save()
                    student.mclass=theClass
                    theClass.save()

            elif k.startswith('classe'):
                    if s.eclass:
                        oldm = Class.objects.get(id=s.eclass.id)
                        #oldm.student_set.remove(student)
                        EnrollDetail.objects.filter(classPtr=oldm, student=student).delete()
                    #theClass.student_set.add(student)
                    ed = EnrollDetail(student=student, classPtr=theClass)
                    ed.save()
                    student.eclass=theClass
                    #print 'add class', student, theClass
                    theClass.save()
    errors=[]
    for s in students:
        print s, s.mclass, s.eclass
        if s.mclass:
            if s.mclass.mandate and ( ('eclass' not in s.__dict__) or s.mclass.mandate!= s.eclass):
                errors.append("%s is required to take %s when taking %s" % (s, s.mclass.mandate, s.mclass))
            elif s.mclass and s.mclass.elective_required and not s.eclass:
                errors.append("%s is required to take an elective class when taking %s." % (s, s.mclass ))

    if errors:    
        return enroll_form(request,errors)

    if 'enroll_paypal' in request.POST:
        return review_tuition_paypal(request)
    if 'enroll_paycheck' in request.POST:
        return review_tuition_check(request)
    #return my_render_to_response(request, 'enroll.html', locals())
    return manage_enrollment(request)
    #return review_tuition(request, 'admin')




def cal_tuition(family, semester, paypal):
    students = family.student_set.order_by("-birthday")
    total = 0
    parent_name = family.parent1FirstName + ' ' + family.parent1LastName
    student_names = ','.join([s.__str__() for s in students])
    enrolled = {}
    for s in students:
        s.total = 0
        s.classes = s.enroll.filter(semester=semester).order_by('elective', 'name')
        s.numClass = len(s.classes)
        for c in s.classes:
            has_mandatory = [cc for cc in s.classes if not cc.elective]
            if has_mandatory:
                c.base = c.discounted_base_cc() if paypal else c.discounted_base_chk()
            else:
                c.base = c.fee.basecc if paypal else c.fee.basechk

            c.total = c.base + c.fee.book + c.fee.material + c.fee.misc
            if c.total > 0:
                enrolled[s.id] = None
            total += c.total
    num_enrolled = len(enrolled)
    discount = semester.feeconfig.get_discount(num_enrolled)
    discount = discount if discount else 0
    reg_fee = semester.feeconfig.familyFee if semester.feeconfig.familyFee else 0
    
    today = datetime.date.today()

    new_family= family.enroll.exclude(semester=semester).count()<=1

    if new_family:
        lateFee= semester.feeconfig.lateFee if (semester.feeconfig.lateDate and today> semester.feeconfig.lateDate) else 0
        total += lateFee
    else:
        lateFee=0
        
    total += reg_fee - discount 
    return locals()

@login_required
def review_tuition_paypal(request):
    return review_tuition(request, 'paypal')

@login_required
def review_tuition_check(request):
    return review_tuition(request, 'check')

import threading
class Email_on_enroll(threading.Thread):
    def __init__(self, request, family, total):
        self.request, self.family, self.total = request, family, total
    def run(self):
        from django.core.mail import send_mail
        from sis.settings import EMAIL_HOST_USER
        try:
            ss=self.request.META['HTTP_ORIGIN']
        except:
            ss='some_site'
        send_mail('New Enrollment: %s  $%.1f' % (self.family.parent1_fullname(), self.total), 
              '%s/family_tuition/%d' % (ss, self.family.id), 
              EMAIL_HOST_USER,
              ['charles.perng@gmail.com'], fail_silently=False)

@login_required
def review_tuition(request, howtopay):
    today = datetime.date.today()
    paypal = howtopay == 'paypal'
    family = request.user.get_profile()
    semester = current_reg_semester() # the semester open for registration
    c = cal_tuition(family, semester, paypal)
    tuition, _created = Tuition.objects.get_or_create(family=family, semester=semester)
    tuition.due = c['total']
    tuition.latest_due_calculation = datetime.date.today()
    tuition.pay_credit = paypal
    tuition.save()
    try:
        c['school_mailing_addr']= Config.objects.get(name='school_mailing_addr').textValue
    except:
        c['school_mailing_addr']= '<school mailing address>'
        
    # print c['school_mailing_addr']

    c['tuition'] = tuition
    c['request'] = request
    c['today'] = today
    #em=Email_on_enroll(request,family, tuition.due)
    #em.run()
    return my_render_to_response(request, 'review_tuition.html', c)

def help(request):
    semester = current_record_semester() # the semester open for registration
    try:
        sis_contact= Config.objects.get(name='sis_contact').emailValue
    except:
        sis_contact = "charles@perng.com"
    try:
        registrar_contact= Config.objects.get(name='registrar_contact').emailValue
    except:
        registrar_contact= "charles@perng.com"
     
    return my_render_to_response(request, 'help.html', locals())


@login_required
def semesterlistx(request):
    semesters = Semester.objects.order_by('id')
    return my_render_to_response(request, 'semesterlist.html', locals())

@login_required
def semesterswitch(request, sem_id):
    semester = Semesters.objects.get(id=decode_id(sem_id))
    request.session['semester']=semester.id
    #return my_render_to_response(request, 'semesterlist.html', locals())
    return HttpResponseRedirect('/')


@login_required
def pastreports(request, sid):
    student = Student.objects.get(id=id_decode(sid))
    #semesters = Semester.object.order__by("id")
    ens = EnrollDetail.objects.filter(student=student).order_by("id")
    ens = [en for en in ens if en.classPtr.recordGrade]
    return my_render_to_response(request, 'pastreports.html', locals())

