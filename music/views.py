import os
import logging


from django.conf import settings
from django.contrib import messages
from django.http import Http404, FileResponse, JsonResponse
from django.shortcuts import render, redirect
from pydub import AudioSegment

from main.models import System
from music.forms import TrackForm
from music.models import Tracks
from music.tasks import start_playback_task, stop_playback_task, check_music_task


def manage(request):
    # view of the music tracks currently in the system.
    music = Tracks.objects.all()
    return render(
        request,
        'manage_music.html',
        {
            'music': music,
        }
    )


def add(request):
    if request.method == 'POST':
        form = TrackForm(request.POST, request.FILES)
        form.uploaded_by = request.user
        if form.is_valid():
            form.save()
            messages.success(request, 'Track added successfully!')
            return redirect('music_manage')  # Redirect after successful form submission

    else:
        form = TrackForm()

    return render(
        request,
        'add_music.html',
        {
            'form': form,
        }
    )


def edit(request):
    return None


def delete(request):
    return None


def preview_track(request, track_id):
    try:
        track = Tracks.objects.get(id=track_id)
        file_path = os.path.join(settings.MEDIA_ROOT, str(track.file_upload.name))

    except Tracks.DoesNotExist:
        raise Http404("Track does not exist")

    # Create a 15-second preview of track starting 60 seconds in.from
    try:
        audio = AudioSegment.from_file(file_path)
        preview_start = 60 * 1000 # 60 seconds.
        preview_end = preview_start + (15 * 1000) # 15 seconds after start
        preview_clip = audio[preview_start:preview_end]

        temp_file_path = os.path.join(settings.MEDIA_ROOT, "previews", f"preview_{track_id}.mp3")
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        preview_clip.export(temp_file_path, format="mp3")
    except Exception as e:
        raise Http404("Error processing track")

    # Serve preview file
    return FileResponse(open(temp_file_path, "rb"), content_type="audio/mpeg")


def start_playback(request):
    """Start the playback task."""
    start_playback_task()
    messages.success(request, 'Playback started!')
    return redirect('home')


def stop_playback(request):
    """Stop the playback task."""
    stop_playback_task()
    # Clear the ID of the task so the interface knows the music has stopped.
    music_loop = System.objects.get(key='music_loop_task')
    music_loop.value = 'False'
    music_loop.save()
    messages.error(request, 'Playback stopped!')
    return redirect('home')


def set_volume(request, vol):
    # This will set the volume and redirect to the home screen.
    volume = System.objects.get(key='volume')
    volume.value = vol
    volume.save()
    logging.info(f"Set volume to {vol}")


def now_playing_refresh(request):
    # This is an AJAX call from the front page that triggers once every 10 seconds. It will
    # refresh the information about what is now playing and the volume level, in the event the track
    # changes, or the volume is changed by another user.

    # Get the current track.
    currently_playing, _ = System.objects.get_or_create(key='now_playing', defaults={'value': 'None'})

    # Check if music is playing
    loop_task, _ = System.objects.get_or_create(key='music_loop_task', defaults={'value': 'False'})
    is_playing = check_music_task(loop_task.value)

    # Get Track Name if playing
    if is_playing and currently_playing != 'None':
        now_playing_track = Tracks.objects.get(id=currently_playing.value).name
    else:
        now_playing_track = 'No Track Playing'

    # Get current volume level
    volume, _ = System.objects.get_or_create(key='volume', defaults={'value': '5'})

    return JsonResponse({
        'now_playing': now_playing_track,
        'volume': int(volume.value),
        'is_playing': is_playing
    })