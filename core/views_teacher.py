
import  copy, datetime
#from django.template.loader import get_template
from django.template import *
#from django.template.defaultfilters import floatformat
#from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string

#from django.shortcuts import render_to_response
#from django.contrib.auth.models import User
#from django.core.context_processors import csrf
#from django.contrib import messages
from django.contrib.auth.decorators import login_required #, user_passes_test
#from django.contrib.admin import widgets
from django.shortcuts import  get_object_or_404, redirect
from sis.core.models import *
from sis.core.forms import *
from sis.core.util import *
from django.contrib.sites.models import Site 


@login_required
def grading_policy(request, cid):
    k='HTTP_HOST'
    print k, request.META[k]
    classid = id_decode(cid)
    school=request.session['school']
    teaches = request.user.get_profile().teaches(school)
    teaches_class_ids = [c.id for c in teaches]
    permitted = classid in teaches_class_ids or request.user.is_superuser
    errors=[]
    if permitted:
        theClass = get_object_or_404(Class,id=classid)
        if request.method == 'POST':
            keys = [tuple(k.split('-') + [request.POST[k]]) for k in request.POST if '-' in k]
            keys = [(l, id_decode(cid), v) for l, cid, v in keys]
            cats = {}
            for label, cid, v  in keys:
                if cid in cats:
                    category = cats[cid]
                else:
                    category = cats[cid] = GradingCategory.objects.get(id=cid)
                    category.hasAssignment = False

                if label == 'category':
                    category.name = v
                elif label == 'weight':
                    if v.isdigit():
                        category.weight = int(v)
                    else:
                        errors.append(v+' is not a number.')
                elif label == 'assignment':
                    category.hasAssignment = True
            for category in cats.values():
                category.save()

        categories = theClass.gradingcategory_set.all()
    else:
        error = 'You are not a teacher of this class'

    return my_render_to_response(request, 'grading_policy.html', locals())


@login_required
def classroaster(request, cid):
    classid = id_decode(cid)
    theClass = get_object_or_404(Class,id=classid)
    students = theClass.student_set.order_by('lastName')
    emails ={}
    for s in students:
        emails[s.family.user.email]=None
        if s.family.altEmail:
            emails[s.family.altEmail]=None
    emails=','.join(emails.keys())
    return my_render_to_response(request, 'classroaster.html', locals())

@login_required
def record(request, class_id):
    classid = id_decode(class_id)
    theClass = get_object_or_404(Class,id=classid)
    categories = theClass.gradingcategory_set.order_by('order')
    return my_render_to_response(request, 'record.html', locals())


@login_required
def record_attendance(request, class_id):
    classid = id_decode(class_id)
    theClass = get_object_or_404(Class, id=classid)
    sessions = theClass.classsession_set.order_by('date')

    return my_render_to_response(request, 'record_attendance.html', locals())

@login_required
def edit_grade(request,  gi_id):
    new=False
    gi=get_object_or_404(GradingItem, id=id_decode(gi_id))
    category=gi.category
    theClass = category.classPtr
    if request.method=='GET':
        ens = theClass.enrolldetail_set.all()
        students = [en.student for en in ens]
        name, date=gi.name, gi.date
        for s in students:
            try:
                s.score=Score.objects.get(student=s, gradingItem=gi).score
            except Exception, e:
                print e
                s.score=''
    
        return my_render_to_response(request, 'edit_grade.html', locals())
    else:
        print request.POST
        try:
            gi.date=datetime.datetime.strptime( request.POST['date'] ,'%m-%d-%y')
        except Exception, e:
            pass
        gi.name = request.POST['name']
        gi.save()

        score_keys =[key for key in request.POST if key.startswith('score')]
        sids = [int(key.split('-')[1]) for key in score_keys]
        for k in score_keys:
            try:
                student=get_object_or_404(Student, id=id_decode(k.split('-')[1]))
                ss=float(request.POST[k])
                score, created=Score.objects.get_or_create(gradingItem=gi, student=student)
                score.score=ss
                score.save()
            except Exception, e:
                print e
                error = 'Grade must be numerical'
        return redirect('record_grade', cat_id=category.eid() )

@login_required
def add_new_grade(request,  cat_id):
    new=True
    category = GradingCategory.objects.get(id=id_decode(cat_id))
    theClass = category.classPtr
    ens = theClass.enrolldetail_set.all()
    students = [en.student for en in ens]
    date=datetime.datetime.today()
    category.gradingitems = category.gradingitem_set.order_by('-id')
    #serial = len(category.gradingitems) + 1
    name = '' # category.name+' '+str(serial)
    if request.method=='POST':
        try:
            date=datetime.datetime.strptime( request.POST['date'] ,'%m-%d-%y')
        except Exception, e:
            date = None
        name = request.POST['name']
        gi = GradingItem(category=category, date=date, name=name)
        gi.save()

        score_keys =[key for key in request.POST if key.startswith('score')]
        sids = [int(key.split('-')[1]) for key in score_keys]
        for k in score_keys:
            try:
                student=get_object_or_404(Student, id=id_decode(k.split('-')[1]))
                s=Score(gradingItem=gi, student=student, score=float(request.POST[k]))
                s.save()
            except Exception, e:
                print e
                error = 'Grade must be numerical'
        print 'no error'
        return redirect('record_grade', cat_id=category.eid() )
    else:
        return my_render_to_response(request, 'edit_grade.html', locals())

@login_required
def record_grade(request,  cat_id):
    print 'record grade'
    category = GradingCategory.objects.get(id=id_decode(cat_id))
    theClass = category.classPtr
    print 'category', category.name
    gis = category.gradingitem_set.order_by('-id')
    return my_render_to_response(request, 'record_grade.html', locals())
    
    

@login_required
def del_attendance(request, cs_id):
    cs_id = id_decode(cs_id)
    cs = ClassSession.objects.get(id=cs_id)
    theClass = cs.classPtr
    for att in cs.attendance_set.all():
        att.delete()
    cs.delete()
    return HttpResponseRedirect('/record_attendance/%s' % (id_encode(theClass.id),))

@login_required
def del_grade(request, gi_id):
    gd_id = id_decode(gi_id)
    gi = GradingItem.objects.get(id=gd_id)
    #theClass = gi.category.classPtr
    gi.delete()
    #calculate_total(request, )
    return redirect('record_grade' , id_encode(gi.category.id))

@login_required
def add_new_attendance(request, class_id):
    print 'add_new_attendance'
    new=True
    theClass= Class.objects.get(id=id_decode(class_id))
    ens = theClass.enrolldetail_set.all()
    students = [en.student for en in ens]
    date=datetime.datetime.today()
    print 'date', date
    if request.method == 'GET':
        return my_render_to_response(request, 'edit_attendance.html', locals())
        assert False
    print request.POST
    try:
        date=datetime.datetime.strptime( request.POST['date'] ,'%m-%d-%y')
    except Exception, e:
        print e
        error= 'Date is required.'
        return my_render_to_response(request, 'edit_attendance.html', locals())
    cs=ClassSession(classPtr=theClass, date=date)
    cs.save()
    for k in request.POST:
        if not k.startswith('att-'):
            continue
        a,sid = k.split('-')
        student = get_object_or_404(Student, pk=id_decode(sid))
        att=Attendance(student=student, session=cs, attended=request.POST[k][0])
        att.save()
    #request.method='GET'
    return redirect('record_attendance', class_id= theClass.eid())



@login_required
def edit_attendance(request, cs_id):
    print 'edit_attendance'
    new=False
    cs=get_object_or_404(ClassSession, id=id_decode(cs_id))
    theClass= cs.classPtr
    ens = theClass.enrolldetail_set.all()
    students = [en.student for en in ens]
    if request.method == 'GET':
        for s in students:
            att, created=Attendance.objects.get_or_create(session=cs, student=s)
            if created:
                att.save()
            s.att=att.attended
        date = cs.date
        print 'date', date
        return my_render_to_response(request, 'edit_attendance.html', locals())

    try:
        cs.date=date=datetime.datetime.strptime( request.POST['date'] ,'%m-%d-%y')
        cs.save()
    except Exception, e:
        print e
        error= 'Date is required.'
        return my_render_to_response(request, 'edit_attendance.html', locals())
    for k in request.POST:
        if not k.startswith('att-'):
            continue
        a,sid = k.split('-')
        student = get_object_or_404(Student, pk=id_decode(sid))
        att=Attendance.objects.get(student=student, session=cs )
        att.attended=attended=request.POST[k][0]
        att.save()
    return redirect( 'record_attendance', class_id=theClass.eid())

    
@login_required
def assignments(request, cat_id):
    cat_id_decoded = id_decode(cat_id)
    category = GradingCategory.objects.get(id=cat_id_decoded)
    if request.method=='POST':
        name=request.POST['Name']
        gi,created=GradingItem.objects.get_or_create(category=category, name=name)
        gi.date=None #request.POST['assign_date']
        gi.duedate=request.POST['due_date']
        gi.assignmentDescr=request.POST['Description']
        try:
            gi.save()
        except:
            gi.duedate=None
            gi.save()

        if created:
            gi.create_download_dir()
    
    due=datetime.datetime.today()+datetime.timedelta(days=7)
    print due 
    assignment_date = DateField().widget.render('assign_date', datetime.datetime.today(), attrs={'id':'assign_date'})
    due_date = DateField().widget.render('due_date', due, attrs={'id':'due_date'})
    

    gditems = GradingItem.objects.filter(category=category).order_by('-id')
    category.serial = len(gditems) + 1
    return my_render_to_response(request, 'assignments.html', locals())

@login_required
def view_assignments(request, cat_id):
    category = get_object_or_404(GradingCategory, id=id_decode(cat_id))
    #gditems = GradingItem.objects.filter(category=category).order_by('-duedate')  
    gditems = GradingItem.objects.filter(category=category).order_by('-id')  
    return my_render_to_response(request, 'view_assignments.html', locals())


@login_required
def new_assignment(request, cid):
    category = GradingCategory.objects.get(id=id_decode(cid))
    gditems = GradingItem.objects.filter(category=category).order_by('-id')
    category.serial = len(gditems) + 1
    if request.method=='POST':
        print request.POST

    return my_render_to_response(request, 'assignment.html', locals())

@login_required
def manage_files(request, aid):
    gi = get_object_or_404(GradingItem, id=id_decode(aid))
    files= gi.get_files()
    return my_render_to_response(request, 'manage_files.html', locals())

@login_required
def del_assignment(request, aid):
    gi = GradingItem.objects.get(id=id_decode(aid))
    category=gi.category
    gi.del_all_homework_files() 
    gi.delete()
    return redirect('assignments', cat_id=category.eid())

@login_required
def del_all_homework_files(request, aid):
    gi = GradingItem.objects.get(id=id_decode(aid))
    category=gi.category    
    gi.del_all_homework_files() 
    return redirect('assignments', cat_id=category.eid())


@login_required
def edit_assignment(request, aid):
    gi = GradingItem.objects.get(id=id_decode(aid))
    if request.method=='POST':
        if 'Delete' in request.POST:
            gi.delete()
        else:
            giform=HomeWorkForm(request.POST, instance=gi)
            #name=request.POST['Name']
            gi.date=None #request.POST['assign_date']
            gi.duedate= datetime.datetime.strptime( request.POST['due_date'] ,'%m-%d-%Y')
            gi.assignmentDescr=request.POST['Description']

            try:   
                gi.save()
            except:
                gi.duedate=None
                gi.save()
                gi.create_download_dir()

        return HttpResponseRedirect('/assignments/'+ gi.category.eid())
    due_date = DateField().widget.render('due_date', gi.duedate, attrs={'id':'due_date'})
    print 'due_date', due_date

    giform=HomeWorkForm(instance=gi)
    request.method='GET'
    return my_render_to_response(request, 'assignment_edit.html', locals())


@login_required
def prepare_report(request, class_id):
    classid = id_decode(class_id)
    theClass = Class.objects.get(id=classid)
    students = theClass.student_set.order_by('lastName')
    for s in students:
        s.enrollment=s.enrolldetail_set.get( classPtr=theClass)
    return my_render_to_response(request, 'prepare_report.html', locals())

@login_required
def evaluation_comment(request, enrolldetail_id):
    en=EnrollDetail.objects.get(id=id_decode(enrolldetail_id))
    if request.method=='GET':
        return my_render_to_response(request, 'evaluation_comment.html', locals())
    en.note = request.POST['comment']
    en.save()
    return prepare_report(request, en.classPtr.eid())

att_dict={'P':'Present', 'A':'Absent', 'L':'Late'}

def get_attendance(student, session):
    try:
        return att_dict[Attendance.objects.get(student=student, session=session).attended]
    except:
        return att_dict['P']
    
def make_rows(data, num):
    if len(data)<= num:
        return [data]
    return [data[0:num]]+ make_rows(data[num:],7)

def get_score(student,item):
    try:
        s= Score.objects.get(student=student, gradingItem=item).score
        if s:
            return s
    except:
        pass
    return 0.0
        
@login_required
def report_card(request, enrolldetail_id):
    en=get_object_or_404(EnrollDetail, id=id_decode(enrolldetail_id))
    theClass=en.classPtr
    student=en.student
    semester = en.classPtr.semester
    sessions=theClass.classsession_set.all()
    num_sessions=len(sessions)
    attendances=[(session.date, get_attendance(student, session)) for session in sessions]
    attendances_rows=make_rows(attendances, 7) if attendances else []
    num_absent =len([a for a in attendances if a[1]=='A'])
    num_late =len([a for a in attendances if a[1]=='L'])
    num_present=num_sessions-num_absent

    categories = theClass.gradingcategory_set.filter(weight__gt= 0)
    student.final_score=0
    for cat in categories:
        items= cat.gradingitem_set.order_by('id')        
        scores=[(item, get_score(student, item) ) for item in items]
        if scores:
            cat.score_rows= make_rows(scores, 7)
        else:
            cat.score_rows=None
        if not scores:
            cat.avg_score=0
        else:
            cat.avg_score = sum([(score[1] if score[1]!=None else 0) for score in scores])/len(scores)
        try:
            cat.class_avg = sum([(item.average if item.average!=None else 0) for item in items])/len(scores)
        except:
            cat.class_avg = 0
        cat.weighted_score = cat.avg_score * cat.weight /100.0
        student.final_score += cat.weighted_score
    
    return my_render_to_response(request, 'reportcard.html', locals())


@login_required
def notify_report_card(request, class_id):
    theClass = Class.objects.get(id=id_decode(class_id))
    site = Site.objects.get_current()
    ens= EnrollDetail.objects.filter(classPtr=theClass)
    for en in ens:
        theClass=en.classPtr
        student=en.student
        subject = render_to_string('report_card_email_subject.txt', locals())
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        
        message = render_to_string('report_card_email.txt', locals())
    
        en.student.family.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
    return generic_message(request, 'Parents Notified', 'teacher', 'Parents have been notified that report cards are ready.' )
