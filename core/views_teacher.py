
import  copy
#from django.template.loader import get_template
from django.template import *
#from django.template.defaultfilters import floatformat
#from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
#from django.shortcuts import render_to_response
#from django.contrib.auth.models import User
#from django.core.context_processors import csrf
#from django.contrib import messages
from django.contrib.auth.decorators import login_required #, user_passes_test
#from django.contrib.admin import widgets

from sis.core.models import *
from sis.core.forms import *
from sis.core.util import *


@login_required
def grading_policy(request, cid):
    k='HTTP_HOST'
    print k, request.META[k]
    classid = id_decode(cid)
    teaches = request.user.get_profile().teaches()
    teaches_class_ids = [c.id for c in teaches]
    permitted = classid in teaches_class_ids or request.user.is_superuser
    errors=[]
    if permitted:
        theclass = Class.objects.get(id=classid)
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

        categories = theclass.gradingcategory_set.all()
    else:
        error = 'You are not a teacher of this class'

    return my_render_to_response(request, 'grading_policy.html', locals())


@login_required
def classroaster(request, cid):
    classid = id_decode(cid)
    theClass = Class.objects.get(id=classid)
    students = theClass.student_set.order_by('lastName')
    return my_render_to_response(request, 'classroaster.html', locals())

@login_required
def record(request, class_id):
    classid = id_decode(class_id)
    theclass = Class.objects.get(id=classid)
    categories = theclass.gradingcategory_set.order_by('order')
    return my_render_to_response(request, 'record.html', locals())


@login_required
def student_attendance(request, class_id, sid):
    theclass = Class.objects.get(id=classid)
    student= Student.objects.get(id=id_decode(sid))
    sessions = theclass.classsession_set.order_by('date')
    for session in sessions:
        try:
            session.att=Attendance.objects.get(student=student, session=session)
        except:
            pass
    return 

@login_required
def record_attendance(request, class_id, show_session):
    classid = id_decode(class_id)
    theclass = Class.objects.get(id=classid)
    students = theclass.student_set.order_by('lastName')
    sessions = theclass.classsession_set.order_by('date')

    if request.method == 'POST':
        print 'attendance post'
        # Update attendance changes
        d = request.POST['extra-att-date'] if 'extra-att-date' in request.POST else request.POST['extra-score-date']
        if '-' in d:
            print 'adding extra'
            year, month, day = tuple(d.split('-'))
            year, month, day = 2000 + int(year[-2:]), int(month), int(day)
            date = datetime.date(year, month, day)

            if 'extra-att-date' in request.POST:
                att_keys = [key for key in request.POST if key.startswith('attextra')]
                att_values = [request.POST[key] for key in att_keys]
                sids = [int(key.split('-')[1]) for key in att_keys]
                session = ClassSession(classPtr=theclass, date=date)
                session.save()
                for sid, att in zip(sids, att_values):
                    student = [s for s in students if  s.id == sid][0]
                    a = Attendance(student=student, session=session, attended=att)
                    a.save()
        att_keys = [key for key in request.POST if key.startswith('att-')]
        att_values = [request.POST[key] for key in att_keys]
        print att_keys, att_values
        att_ids = [int(key.split('-')[1]) for key in att_keys]

        for iid, value in zip(att_ids, att_values):
            att = Attendance.objects.get(id=iid)
            if att.attended != value:
                att.attended = value
                att.save()


    if sessions:
        sno = len(sessions)

        show_session = sno - 1 if show_session == '_' else int(show_session)
        snom1 = max(0, show_session - 1)
        snop1 = min(sno - 1, show_session + 1)
        print 'snom1, snop1', snom1, snop1
        sessions = [sessions[show_session]]
    else:
        snom1 = 0
        snop1 = 0
        print 'snom1, snop1', snom1, snop1
        session = []


    for s in students:
        atts = [Attendance.objects.get_or_create(student=s, session=session)[0] for session in sessions] #there maybe students added after previous record
        s.att_fields = [forms.Select(choices=ATT_CHOICES).render('att-%d' % (a.id,), a.attended) for a in atts]
        s.extra_att = forms.Select(choices=ATT_CHOICES).render('attextra-' + str(s.id), '')
    #extra_att_date=DateField(widget = widgets.AdminDateWidget).widget.render('extra-att-date',datetime.datetime.today())
    #extra_att_date=DateField(widget = widgets.AdminDateWidget).widget.render('extra-att-date',datetime.datetime.today(),attrs={'id':'extra_att_date'})
    extra_att_date = DateField().widget.render('extra-att-date', datetime.datetime.today(), attrs={'id':'extra_att_date'})

    return my_render_to_response(request, 'record_attendance.html', locals())

@login_required
def record_grade(request, class_id, cat_id, show_item):
    print 'record grade'
    classid = id_decode(class_id)
    theclass = Class.objects.get(id=classid)
    category = GradingCategory.objects.get(id=id_decode(cat_id))
    print 'category', category.name
    students = theclass.student_set.order_by('lastName')

    if request.method == 'POST':
        score_item_changed = {}
        print request.POST
        d = request.POST['extra-score-date']
        if '-' in d:
            print 'adding extra'
            year, month, day = tuple(d.split('-'))
            year, month, day = 2000 + int(year[-2:]), int(month), int(day)
            date = datetime.date(year, month, day)
            if 'extra-score-date' in request.POST:
                print 'extra-score-date'
                category = GradingCategory.objects.get(id=id_decode(cat_id))
                score_keys = [key for key in request.POST if key.startswith('scoreextra')]
                score_values = [float(request.POST[key]) if key in request.POST and request.POST[key].isdigit() else 0  for key in score_keys]
                ids = [int(key.split('-')[1]) for key in score_keys]
                gding = GradingItem(category=category, date=date, name=request.POST['extra-score-name'])
                gding.save()
                for sid, score in zip(ids, score_values):
                    student = [s for s in students if  s.id == sid][0]
                    g = Score(student=student, gradingItem=gding, score=score)
                    g.save()
                    score_item_changed[gding.id] = gding
        # Update score changes
        score_keys = [key for key in request.POST if key.startswith('score-')]
        score_values = [request.POST[key] for key in score_keys]
        score_ids = [int(key.split('-')[1]) for key in score_keys]
        for iid, value in zip(score_ids, score_values):
            score = Score.objects.get(id=iid)
            if score.score != value:
                score.score = value
                score.save()
                gding = score.gradingItem
                score_item_changed[gding.id] = gding
        # update aggregates
        for i, g in score_item_changed.iteritems():
            ss = [score.score for score in g.score_set.all()]
            g.highest = max(ss)
            g.lowest = min(ss)
            g.average = sum(ss) / len(ss)
            g.median = getMedian(ss)
            g.save()

    #data for score
    category.students = [copy.copy(s) for s in students] # make a copy of students
    category.gradingitems = category.gradingitem_set.order_by('date')
    category.serial = len(category.gradingitems) + 1
    for s in category.students:
        scores=[]
        for g in category.gradingitems:
            score, created=Score.objects.get_or_create(student=s, gradingItem=g)
            if created or not score.score:
                score.score=0
            scores += [score]
        s.scores = [forms.FloatField(min_value=0, max_value=120).widget.render('score-' + str(score.id), ('%f' % (score.score,)).rstrip('0').rstrip('.')) for score in scores]
        s.extra_score = forms.FloatField(min_value=0, max_value=120).widget.render('scoreextra-%d' % (s.id,), None)

    return my_render_to_response(request, 'record_grade.html', locals())



@login_required
def del_attendance(request, cs_id):
    cs_id = id_decode(cs_id)
    cs = ClassSession.objects.get(id=cs_id)
    theClass = cs.classPtr
    for att in cs.attendance_set.all():
        att.delete()
    cs.delete()
    return HttpResponseRedirect('/record_attendance/%s/_' % (id_encode(theClass.id),))

@login_required
def del_score(request, gd_id):
    gd_id = id_decode(gd_id)
    gd = GradingItem.objects.get(id=gd_id)
    theClass = gd.category.classPtr
    for score in gd.score_set.all():
        score.delete()
    gd.delete()
    return HttpResponseRedirect('/record_grade/%s/%s/_' % (id_encode(theClass.id),id_encode(gd.category.id)))


@login_required
def calculate_total(request, class_id, calculate=False):
    request.session['show_stats'] = 'show_stats' in request.POST
    class_id = id_decode(class_id)
    theclass = Class.objects.get(id=class_id)
    theclass.total_ready = 'total_ready' in request.POST


    categories = theclass.gradingcategory_set.all()
    students = theclass.student_set.all()
    for s in students:
        s.ed = EnrollDetail.objects.get(student=s, classPtr=theclass)
        s.ed.final_score = 0
        for c in categories:
            gis = c.gradingitem_set.all()
            for gi in gis:
                gi_len = len(gis)
                if not gi_len:
                    break
                s.ed.final_score += c.weight * sum([sc.score for sc in Score.objects.filter(student=s, gradingItem=gi)]) / gi_len / 100
    scores = [s.ed.final_score for s in students]
    scores.sort(reverse=True)
    for s in students:
        s.ed.rank = scores.index(s.ed.final_score) + 1
        s.ed.save()
    cat_id = request.POST['category']
    print request.POST
    print 'cat_id', cat_id
    return HttpResponseRedirect('/record_grade/%s/%s/0' % (theclass.eid(), cat_id))


@login_required
def assignments(request, cat_id):
    cat_id_decoded = id_decode(cat_id)
    category = GradingCategory.objects.get(id=cat_id_decoded)
    if request.method=='POST':
        print request.POST
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
    

    gditems = GradingItem.objects.filter(category=category).order_by('-duedate')
    category.serial = len(gditems) + 1
    return my_render_to_response(request, 'assignments.html', locals())

@login_required
def view_assignments(request, cat_id):
    category = GradingCategory.objects.get(id=id_decode(cat_id))
    gditems = GradingItem.objects.filter(category=category).order_by('-duedate')  
    return my_render_to_response(request, 'view_assignments.html', locals())


@login_required
def new_assignment(request, cid):
    category = GradingCategory.objects.get(id=id_decode(cid))
    gditems = GradingItem.objects.filter(category=category).order_by('duedate')
    category.serial = len(gditems) + 1
    if request.method=='POST':
        print request.POST

    return my_render_to_response(request, 'assignment.html', locals())


@login_required
def edit_assignment(request, aid):
    gi = GradingItem.objects.get(id=id_decode(aid))
    if request.method=='POST':
        if 'Delete' in request.POST:
            gi.delete()
        else:
            giform=HomeWorkForm(request.POST, instance=gi)
            if giform.is_valid():
                try:   
                    gi.save()
                except:
                    gi.duedate=None
                    gi.save()
                gi.create_download_dir()

        return HttpResponseRedirect('/assignments/'+ gi.category.eid())
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
    return [data[0:num]]+ make_rows(data[num:])

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
    en=EnrollDetail.objects.get(id=id_decode(enrolldetail_id))
    theClass=en.classPtr
    student=en.student
    semester = en.classPtr.semester
    sessions=theClass.classsession_set.all()
    num_sessions=len(sessions)
    attendances=[(session.date, get_attendance(student, session)) for session in sessions]
    attendances_rows=make_rows(attendances, 7)
    num_absent =len([a for a in attendances if a[1]=='A'])
    num_late =len([a for a in attendances if a[1]=='L'])
    num_present=num_sessions-num_absent

    categories = theClass.gradingcategory_set.filter(weight__gt= 0)
    student.final_score=0
    for cat in categories:
        items= cat.gradingitem_set.all()        
        scores=[(item, get_score(student, item) ) for item in items]
        print scores
        cat.score_rows= make_rows(scores, 7)
        if not scores:
            cat.avg_score=0
        else:
            cat.avg_score = sum([score[1] for score in scores])/len(scores)
        cat.class_avg = sum([item.average for item in items])/len(scores)

        cat.weighted_score = cat.avg_score * cat.weight /100.0
        student.final_score += cat.weighted_score
    
    return my_render_to_response(request, 'reportcard.html', locals())


