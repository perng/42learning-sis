from django.core.context_processors import csrf
from django.shortcuts import render_to_response

from django.conf import settings
from django.http import HttpResponseRedirect
import datetime
import logging

logging.basicConfig(filename='/tmp/sis.log',level=logging.INFO)



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

    if not new_family:
        lateFee= semester.feeconfig.lateFee if (semester.feeconfig.lateDate and today> semester.feeconfig.lateDate) else 0
        total += lateFee
    else:
        lateFee=0
        
    total += reg_fee - discount 
    return locals()


def secure_required(view_func):
    """Decorator makes sure URL is accessed over https."""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.is_secure():
            if getattr(settings, 'HTTPS_SUPPORT', True):
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(secure_url)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


    

def my_render_to_response(request,template,c):
    c.update(csrf(request))
    return render_to_response(template, c)    

def generic_message(request, title, view, message):
    return render_to_response('generic_message.html', locals())

def getMedian(numericValues):
    theValues = sorted(numericValues)
    if len(theValues) % 2 == 1:
        return theValues[(len(theValues) + 1) / 2 - 1]
    else:
        lower = theValues[len(theValues) / 2 - 1]
        upper = theValues[len(theValues) / 2]
    return (float(lower + upper)) / 2


def lookup(iid, objects):
    for o in objects:
        if iid == o.id:
            return o
    return None

import random, math

def scrambledigits(n):
    return ''.join([random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']) for i in range(n)])

def id_encode(aid):
    en = lambda x: x * x + random.randint(0, x)
    n = 0
    while aid < 1000:
        aid = en(aid)
        n += 1
    eid1 = str(aid)
    return scrambledigits(len(eid1)) + eid1 + scrambledigits(len(eid1)) + str(n)
    #return scrambledigits(len(eid1))+eid1+scrambledigits(len(eid1))+'_'+str(n)

def id_decode(did):
    # admin backdoor 
    if did[0]=='s':
        return int(did[1:])
    de = lambda x: math.floor(math.sqrt(x))
    #did1,m=tuple(did.split('_'))
    r = len(did) % 3
    if not r:
        return -1
    #logging.info('did-r='+str(did[-r:]))
    m = int(str(did[-r:]))
    
    m = int(m)
    n = len(did) / 3
    did1 = did[n:(2 * n)]
    did2 = int(did1)
    for mm in range(m):
        did2 = int(de(did2))
    return did2


def median(data):
    num = len(data)
    if num == 0:
        return 0
    if num % 2 == 1: 
        data[(num-1)/2]
    else:
        if num ==1:
            return data[0]
        else: 
            return (data[num/2]+data[num/2-1])/2


if __name__ == '__main__':
    for i in range(10000):
        x = random.randint(1, 1000)
        a = id_encode(x)
        b = id_decode(a)
        assert x == b
        print a, b
    #print 10000, id_encode(10000) , id_decode(id_encode(10000))
    #print 1, id_encode(1) , id_decode(id_encode(1))
