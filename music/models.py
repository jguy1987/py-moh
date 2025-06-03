from django.db import models

class Tracks(models.Model):
    name = models.CharField(max_length=200)
    file_upload = models.FileField(upload_to='/media')
    upload_date = models.DateTimeField(auto_now_add=True)
    upload_by = models.CharField(max_length=200)
    active = models.BooleanField(default=True, help_text='Active Track?')

