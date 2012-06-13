from sis.core.models import  *

school_mailing_addr, _created = Config.objects.get_or_create(name='school_mailing_addr',
                                    verbose_name='School Mailing Address', valueType='text')
sis_contact,_created= Config.objects.get_or_create(name='sis_contact',
                                    verbose_name='SIS System Admin Email', valueType='email')
registrar_contact,_created= Config.objects.get_or_create(name='registrar_contact',
                                    verbose_name='Registrar Email', valueType='email')
    
