from sis.core.models import  *

gcs=GradingCategory.objects.all()

d={}

for gc in gcs:
    if (gc.classPtr.id, gc.name) in d:
        gc.delete()
    else:
        d[(gc.classPtr.id, gc.name)]=None
        