import os
hostname=os.uname()[1]
if hostname=='sis':
    site_static_path = 'https://sis.nwcsny.org/static'
elif hostname=='sisdemo':
    site_static_path = 'https://demo.learning42.com/static'
else:
    site_static_path = '/static'
    #site_static_path = 'http://localhost:8000/static'
#site_static_path = 'http://static.nwcsny.org'
