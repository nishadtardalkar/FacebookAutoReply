from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from . import monitor_and_reply
from fbreply.CustomDjango import basehttp

def index(request):
    return render(request, 'index.html', {})

@csrf_exempt
def start(request):
    data = request.POST.get('data', '')
    r = monitor_and_reply.start_monitor('{"data":' + data + '}')
    return HttpResponse(str(r))

@csrf_exempt
def abort(request):
    monitor_and_reply.stop_monitor()
    return HttpResponse('0')

@csrf_exempt
def status(request):
    s = monitor_and_reply.get_status()
    return HttpResponse(str(s))
