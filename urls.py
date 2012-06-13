from django.conf.urls import patterns, include, url
from django.views.generic import ListView
from sis.core.views import *
from sis.core.views_parent import *
from sis.core.views_teacher import *
from sis.core.views_admin import *

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin as aadmin
#aadmin.autodiscover()

urlpatterns = patterns('',
     # General
     url(r'^$', home, name='home'),
     #url(r'^index$', home, name='index'),
     url(r'^change_view/(?P<view>.+)$', change_view, name='change_view'),

     url(r'^offered_classes', offered_classes, name='offered_classes'),

     # Parent
     url(r'^enroll_form$', enroll_form, name='enroll_form'),
     url(r'^enroll$', enroll, name='enroll'),
     url(r'^familyinfo$', familyinfo, name='familyinfo'),
     url(r'^users/(?P<uid>.+)/$', user_profile, name='user_profile'),     
     url(r'^family_tuition/(?P<fid>.+)$', family_tuition, name='family_tuition'),
     url(r'^edit_student$', edit_student, name='edit_student'),
     url(r'^edit_student/(?P<sid>.+)$', edit_student, name='edit_student'),
     url(r'^student_score/(?P<sid>.+)$', student_score, name='student_score'),
     url(r'^review_tuition_paypal$', review_tuition_paypal, name='review_tuition_paypal'),
     url(r'^review_tuition_check$', review_tuition_check, name='review_tuition_check'),

     # Teacher

     url(r'^grading_policy/(?P<cid>.+)$', grading_policy, name='grading_policy'),
     url(r'^classroaster/(?P<cid>.+)$', classroaster, name='classroaster'),
     url(r'^record/(?P<class_id>.+)$', record, name='record'),
     url(r'^record_attendance/(?P<class_id>.+)/(?P<show_session>.+)$', record_attendance, name='record_attendance'),
     url(r'^student_attendance/(?P<class_id>.+)/(?P<sid>.+)$', student_attendance, name='student_attendance'),

     
     url(r'^record_grade/(?P<class_id>.+)/(?P<cat_id>.+)/(?P<show_item>.+)$', record_grade, name='record_grade'),
     url(r'^accounts/profile', profile, name='profile'),
     #(r'^accounts/', include('sis.registration.urls')),
     (r'^accounts/', include('registration.backends.default.urls')),
     url(r'^del_attendance/(?P<cs_id>.+)$', del_attendance, name='del_attendance'),
     url(r'^del_score/(?P<gd_id>.+)$', del_score, name='del_score'),
     url(r'^calculate_total/(?P<class_id>.+)$', calculate_total, name='calculate_total'),
     url(r'^assignments/(?P<cat_id>.+)$', assignments, name='assignments'),
     url(r'^view_assignments/(?P<cat_id>.+$)', view_assignments, name='view_assignments'),
     url(r'^new_assignment/(?P<class_id>.+$)', new_assignment, name='new_assignment'),

     # Admin
     url(r'^semester$', semesters, name='semesters'),
     url(r'^edit_semester$', edit_semester, name='edit_semester'),
     url(r'^edit_semester/(?P<sem_id>[0-9]+)$', edit_semester, name='edit_semester'),
     url(r'^semester/(?P<sid>[0-9]+)$', semester, name='semester'),
     url(r'^semesterlist$', semesterlist, name='semesterlist'),
     url(r'^classlist/(?P<sem_id>[0-9]+)$', classlist, name='classlist'),
     url(r'^edit_class$', edit_class, name='edit_class'),
     url(r'^edit_class/(?P<class_id>[0-9]+)$', edit_class, name='edit_class'),
     url(r'^delete_class/(?P<class_id>[0-9]+)$', delete_class, name='delete_class'),
     url(r'^payment$', payment, name='payment'),
     url(r'^unpaid_payment$', unpaid_payment, name='unpaid_payment'),

     url(r'^3.14159sisadmin', sisadmin, name='sisadmin'),
     url(r'^sisadmincmd/(?P<adminid>.+)/(?P<command>.*)/(?P<subject>.*)$', sisadmin, name='sisadmin'),
     url(r'^active_directory', active_directory, name='active_directory'),
     url(r'^teacher_directory', teacher_directory, name='teacher_directory'),
     url(r'^family_directory/$', ListView.as_view(model=Family ), name='family_directory'),
     url(r'^sys_config/', system_config, name='sys_config'),
     url(r'^help/', help, name='help'),
    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(aadmin.site.urls)),


)
