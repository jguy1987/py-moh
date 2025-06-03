from django import forms
from music.models import Tracks


class TrackForm(forms.ModelForm):
    class Meta:
        model = Tracks
        fields = ['name', 'file_upload', 'active']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Track Name'}),
            'file_upload': forms.FileInput(attrs={'class': 'form-control', 'accept': '.mp3, .wav'}),
            'upload_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Uploaded By'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_file_upload(self):
        file = self.cleaned_data.get('file_upload')
        if not file.name.endswith(('.mp3', '.wav')):
            raise forms.ValidationError("Only .mp3 or .wav files are allowed.")
        return file
