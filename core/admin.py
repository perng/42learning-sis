from django.contrib import admin
from django.contrib.sites.models import Site
from sis.core.models import *

#class SiteAdmin(admin.ModelAdmin):
#    pass
#admin.site.register(Site, SiteAdmin)

for model in [School, Role,Family, Semester, Class, Student, EnrollDetail,Award, 
              GradingCategory,GradingItem,Score,ClassSession,Attendance,Fee, FeeConfig,
              Tuition,Config, RegistrationHistory ]:
    admin.site.register(model)
