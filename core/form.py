from django import forms
from django.forms import ModelForm
from django.db import models
from .models import Causa


class ImageUploadForm(forms.Form):
    image = forms.ImageField()


