from django.core.context_processors import csrf
from django.shortcuts import render_to_response

from django.conf import settings
from django.http import HttpResponseRedirect

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
    de = lambda x: math.floor(math.sqrt(x))
    #did1,m=tuple(did.split('_'))
    r = len(did) % 3
    m = int(did[-r:])
    
    m = int(m)
    n = len(did) / 3
    did1 = did[n:(2 * n)]
    did2 = int(did1)
    for mm in range(m):
        did2 = int(de(did2))
    return did2

if __name__ == '__main__':
    for i in range(10000):
        x = random.randint(1, 1000)
        a = id_encode(x)
        b = id_decode(a)
        assert x == b
        print a, b
    #print 10000, id_encode(10000) , id_decode(id_encode(10000))
    #print 1, id_encode(1) , id_decode(id_encode(1))
