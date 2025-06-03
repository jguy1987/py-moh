
# from django.contrib import admin
from django.urls import path
from main import views as main_view
from music import views as music_view

urlpatterns = [
    path('', main_view.home, name='home'),
    path('music/manage', music_view.manage, name='music_manage'),
    path('music/add', music_view.add, name='add_music'),
    path('music/edit/<int:id>', music_view.edit, name='edit_track'),
    path('music/delete/<int:id>', music_view.delete, name='delete_track'),
    path('preview/<int:track_id>/', music_view.preview_track, name='preview_track'),
    path('music/start', music_view.start_playback, name='start_playback'),
    path('music/stop', music_view.stop_playback, name='stop_playback'),
    #    path('admin/', admin.site.urls),
]
