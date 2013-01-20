from django.conf.urls import patterns, include, url
from django.views.generic import ListView
from sis.core.views import *
from sis.core.views_parent import *
from sis.core.views_teacher import *
from sis.core.views_admin import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin as aadmin
aadmin.autodiscover()

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
     url(r'^add_grading_category/(?P<cid>.+)$', add_grading_category, name='add_grading_category'),
     url(r'^classroaster/(?P<cid>.+)$', classroaster, name='classroaster'),
     url(r'^record/(?P<class_id>.+)$', record, name='record'),
     url(r'^record_attendance/(?P<class_id>.+)$', record_attendance, name='record_attendance'),

     url(r'^record_grade/(?P<cat_id>.+)$', record_grade, name='record_grade'),
     url(r'^add_new_grade/(?P<cat_id>.+)$', add_new_grade, name='add_new_grade'),
     url(r'^edit_grade/(?P<gi_id>.+)$', edit_grade, name='edit_grade'),
     url(r'^del_grade/(?P<gi_id>.+)$', del_grade, name='del_grade'),

     #url(r'^prepare_report/(?P<class_id>.+)$', prepare_report, name='prepare_report'),
     url(r'^evaluation_comment/(?P<enrolldetail_id>.+)$', evaluation_comment, name='evaluation_comment'),

     url(r'^accounts/profile', profile, name='profile'),
     #(r'^accounts/', include('sis.registration.urls')),
     (r'^accounts/', include('sis.registration.backends.default.urls')),
     url(r'^del_attendance/(?P<cs_id>.+)$', del_attendance, name='del_attendance'),
     url(r'^edit_attendance/(?P<cs_id>.+)$', edit_attendance, name='edit_attendance'),

     url(r'^add_new_attendance/(?P<class_id>.+$)', add_new_attendance, name='add_new_attendance' ),

     #url(r'^calculate_total/(?P<class_id>.+)$', calculate_total, name='calculate_total'),
     url(r'^assignments/(?P<cat_id>.+)$', assignments, name='assignments'),
     url(r'^assignment_edit/(?P<aid>.+)$', edit_assignment, name='assignment_edit'),
     url(r'^manage_files/(?P<aid>.+)$', manage_files, name='manage_files'),

     url(r'^del_assignment/(?P<aid>.+)$', del_assignment, name='del_assignment'),
     url(r'^del_all_homework_files/(?P<aid>.+)$', del_all_homework_files, name='del_all_homework_files'),

     url(r'^view_assignments/(?P<cat_id>.+$)', view_assignments, name='view_assignments'),
     url(r'^new_assignment/(?P<class_id>.+$)', new_assignment, name='new_assignment'),
     url(r'^evaluation_comment/(?P<enrolldetail_id>.+$)', evaluation_comment, name='evaluation_comment'),
     url(r'^report_card/(?P<enrolldetail_id>.+$)', report_card, name='report_card'),
     url(r'^notify_report_card/(?P<class_id>.+$)', notify_report_card, name='notify_report_card'),
     url(r'^toggle_final_grade_ready/(?P<class_id>.+$)', toggle_final_grade_ready, name='toggle_final_grade_ready'),

     url(r'^grade_summaries/(?P<sem_id>[0-9]+)$', report_summaries, name='report_summaries'),
     url(r'^grade_summary/(?P<class_id>[0-9]+)$', report_summary, name='report_summary'),
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
     url(r'^class_enrollment$', class_enrollment, name='class_enrollment'),
     url(r'^unpaid_payment$', unpaid_payment, name='unpaid_payment'),
     url(r'^class_enrollment$', class_enrollment, name='class_enrollment'),

     url(r'^3.14159sisadmin', sisadmin, name='sisadmin'),
     url(r'^sisadmincmd/(?P<adminid>.+)/(?P<command>.*)/(?P<subject>.*)$', sisadmin, name='sisadmin'),
     url(r'^active_directory', active_directory, name='active_directory'),
     url(r'^teacher_directory', teacher_directory, name='teacher_directory'),
     url(r'^family_directory/$', ListView.as_view(model=Family ), name='family_directory'),
     url(r'^sys_config/', system_config, name='sys_config'),
     url(r'^help/', help, name='help'),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(aadmin.site.urls)),


)
