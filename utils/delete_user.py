import sys
from sis.core.models import Family
from django.contrib.auth.models import User

family_id = int(sys.argv[1])
f=Family.objects.get(id=family_id)

u=f.user
u.delete()
