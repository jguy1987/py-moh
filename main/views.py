from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from main.models import System
from music.models import Tracks

from music import tasks as music_tasks

@login_required
def home(request):
    default_system = {
        'value': 'False',
    }
    loop_task, _ = System.objects.get_or_create(key='music_loop_task', defaults=default_system)
    # double check that the task is actually running...
    if not music_tasks.check_music_task(loop_task.value):
        task_running = 'False'
    else:
        task_running = 'True'
    default_now_playing = {
        'value': 'None',
    }
    currently_playing, create = System.objects.get_or_create(key='now_playing', defaults=default_now_playing)
    if create or currently_playing.value == 'None':
        now_playing_track = 'No Track Playing'
    else:
        # get the track name from the currently_playing value
        now_playing_track = Tracks.objects.get(id=currently_playing.value).name

    # Get the current volume
    volume, _ = System.objects.get_or_create(key='volume', defaults={'value': '5'})
    return render(
        request,
        'home.html',
        {
            'loop_task': task_running,
            'currently_playing': now_playing_track,
            'current_volume': int(volume.value),
        }
    )


def login(request):
    # Displays admin login page, with a redirect to the home page
    redirect_url = reverse('home')  # Replace with your target URL
    login_url = reverse('admin:login')  # Reverse-resolves the admin login URL
    return redirect(f"{login_url}?next={redirect_url}")



@login_required
def logout(request):
    from django.contrib.auth import logout

    # Logs the user out.
    logout(request)
    return redirect('login')