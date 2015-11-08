from math import floor, sqrt
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


def my_render_to_response(request, template, c):
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
  return ''.join(
    [random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']) for i in
     range(n)])


def id_encode(aid):
  en = lambda x: x * x + random.randint(0, x)
  n = 0
  while aid < 1000:
    aid = en(aid)
    n += 1
  eid1 = str(aid)
  return scrambledigits(len(eid1)) + eid1 + scrambledigits(len(eid1)) + str(n)


def id_decode(did):
  de = lambda x: math.floor(math.sqrt(x))
  r = len(did) % 3
  if not r:
    return -1
  m = int(did[-r:])

  m = int(m)
  n = len(did) / 3
  did1 = did[n:(2 * n)]
  did2 = int(did1)
  for _mm in range(m):
    did2 = int(de(did2))
  return did2


def median(data):
  num = len(data)
  if num == 0:
    return 0
  if num % 2 == 1:
    data[(num - 1) / 2]
  else:
    if num == 1:
      return data[0]
    else:
      return (data[num / 2] + data[num / 2 - 1]) / 2

def det_encode(aid):
  x = str((2 * aid + 31) ** 2 + 79)
  return x[::-1]

def det_decode(aid):
  aid = str(aid)[::-1]
  aid = int(aid)
  aid -= 79
  return (int(sqrt(aid) + 0.5) - 31) / 2

if __name__ == '__main__':
  for i in range(100000):
    if i != det_decode(det_encode(i)):
      print i


def get_school():
  return School.objects.all()[0]