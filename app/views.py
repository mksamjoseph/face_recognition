from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

def home(request):
    # Render the page with your video + websocket client code
    return render(request, "app1/start.html")

@xframe_options_exempt
def camera2_view(request):
    return render(request, 'app1/camera2.html')


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def landingpage(request):
    return render(request,'app1/landingpage.html')

def logout_user(request):
    logout(request)
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        pwd = request.POST.get('password')
        user = authenticate(request, username=uname, password=pwd)
        if user is not None:
            login(request, user)
            return redirect('dash')  # ✅ name of your dashboard view
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'app1/login.html')


def dashboarad(request):
    return render(request,'app1/start.html')
def feature(request):
    return render(request,'app1/feature.html')
def team(request):
    return render(request,'app1/team.html')
def camera(request):
    return render(request,'app1/camera2.html')

def live_feed(request):
    return render(request, 'app1/login.html')

# views.py
from django.http import JsonResponse
from .models import PersonSighting

def get_initial_logs(request):
    logs = PersonSighting.objects.select_related('known_person', 'unknown_person')[:50]
    
    data = []
    for log in logs:
        person_name = log.known_person.name if log.known_person else log.unknown_person.name
        status = 'known' if log.known_person else 'unknown'
        data.append({
            "person": person_name,
            "camera": log.location,
            "time": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
        })

    return JsonResponse({"logs": data})

from django.utils.timezone import now
from datetime import timedelta
from .models import PersonSighting

def get_stats(request):
    total = PersonSighting.objects.count()
    known = PersonSighting.objects.filter(known_person__isnull=False).count()
    alerts = PersonSighting.objects.filter(unknown_person__isnull=False).count()

    # Count all sightings in the last 60 seconds
    last_minute = now() - timedelta(minutes=1)
    recent_count = PersonSighting.objects.filter(timestamp__gte=last_minute).count()

    return JsonResponse({
        "known_percent": round((known / total) * 100 if total > 0 else 0, 2),
        "alerts": alerts,
        "person_count": recent_count
    })

from django.http import JsonResponse
from django.db.models import Count
from .models import KnownPerson, UnknownPerson, PersonSighting
from django.db.models import Avg

def get_stat(request):
    total_detections = PersonSighting.objects.count()
    known_detections = PersonSighting.objects.filter(known_person__isnull=False).count()
    alerts = PersonSighting.objects.filter(unknown_person__isnull=False).count()

    avg_latency = PersonSighting.objects.aggregate(avg_latency=Avg('latency'))['avg_latency'] or 0

    if total_detections == 0:
        known_percentage = 0
    else:
        known_percentage = round((known_detections / total_detections) * 100, 2)

    return JsonResponse({
        "known_percentage": known_percentage,
        "alerts": alerts,
        "person_count": total_detections,
        "avg_latency": round(avg_latency, 3)
    })
