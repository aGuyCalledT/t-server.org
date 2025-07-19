from django import forms
from .models import Movie
from .models import ContactMessage

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'year']
        labels = {
            'title': "Title",
            'year': "Year"}


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        labels = {
            'name': "Your Name",
            'email': "Your Email",
            'message': "Your Message",
        }
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }
