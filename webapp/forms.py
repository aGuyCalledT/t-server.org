from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Your Name", required=True)
    email = forms.EmailField(label="Your Email", required=True)
    message = forms.CharField(widget=forms.Textarea, label="Your Message", required=True)

class MovieForm(forms.Form):
    title = forms.CharField(max_length=200, label="Movie Title", required=True)
    year = forms.CharField(max_length=4, label="Release Year (optional)", required=False)
