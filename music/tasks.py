import random
import time
import pygame
from django_q.models import OrmQ

from main.models import System
from music.models import Tracks
import logging


# Get logger
logger = logging.getLogger(__name__)


def playback_should_stop():
    """Check if playback should stop."""
    defaults = {
        'value': 'False',
    }
    ret, _ = System.objects.get_or_create(key='STOP_PLAYBACK_FLAG', defaults=defaults)
    if ret.value == 'True':
        return True
    else:
        return False


def get_volume():
    """Get the correct value of the volume of the playback"""
    ret, _ = System.objects.get_or_create(key='volume', defaults={'value': '5'})
    return int(ret.value)


def clear_stop_flag():
    """Clear the stop flag to allow playback to resume."""
    defaults = {
        'value': 'False',
    }
    ret, _ = System.objects.update_or_create(key='STOP_PLAYBACK_FLAG', defaults=defaults)
    if ret.value == 'True':
        ret.value = 'False'
        ret.save()
    else:
        pass



def run_player_task():
    """
    Task to run an indefinite background loop for shuffling and playing active tracks.
    :return:
    """
    logging.info('Player Started.')
    try:
        while True:
            if playback_should_stop():
                pygame.mixer.quit()
                return

            active_tracks = Tracks.objects.filter(
                active=True,
            ).order_by('?')  # Shuffle tracks

            logger.info('Playlist generated.')

            if not active_tracks.exists():
                logger.info("No active tracks to play. Waiting...")
                time.sleep(10)  # Wait before checking again
                continue

            # Shuffle and play each track
            for track in active_tracks:
                if playback_should_stop():
                    pygame.mixer.quit()
                    logging.info("Playback should stop. Stopping.")
                    return
                pygame.mixer.music.set_volume(get_volume())

                play_track(track)
    except Exception as e:
        logging.error(f"Error running player task: {e}")
    finally:
        pygame.mixer.quit()


def play_track(track):
    """
    Play a single track using pygame.
    :param track: Track instance
    """
    pygame.mixer.init()
    logging.info("Player initialized.")
    try:
        pygame.mixer.quit()
        pygame.mixer.init()
        # Before loading a new track, clean up the previous one.
        logging.info(f"Playing track: {track.name}")
        pygame.mixer.music.load(track.file_upload.path)
        pygame.mixer.music.play()

        defaults = {
            'value': track.id,
        }
        now_playing, _ = System.objects.update_or_create(key='now_playing', defaults=defaults)

        # Wait until the track finishes playing
        while pygame.mixer.music.get_busy():
            if playback_should_stop():
                pygame.mixer.music.stop()
                return  # Stop immediately if playback is flagged
            time.sleep(1)

    except Exception as e:
        logging.error(f"Error playing track {track.name}: {e}")
    finally:
        pygame.mixer.quit()


def start_playback_task():
    """Invoke this to start the playback task."""
    from django_q.tasks import async_task

    clear_stop_flag()
    # Store the ID of the task so that we can recall it for status displays, just in case the task crashes.
    task_id = async_task('music.tasks.run_player_task')

    default_system = {
        'value': task_id,
    }
    task, _ = System.objects.update_or_create(key='music_loop_task', defaults=default_system)



def stop_playback_task():
    """Stop the playback task."""
    defaults = {
        'value': 'True',
    }
    task, _ = System.objects.update_or_create(key='STOP_PLAYBACK_FLAG', defaults=defaults)
    # clear the ormq table.
    OrmQ.objects.all().delete()


def check_music_task(t_id):
    tasks = []

    for i in OrmQ.objects.all():
        # deserialize
        tasks.append(i.task_id())

    if t_id in tasks:
        return True
    else:
        return False