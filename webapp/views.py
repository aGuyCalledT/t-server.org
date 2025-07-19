from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings # Wird noch benötigt, aber CSV_FILE_PATH nicht mehr
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.db import IntegrityError # Neu für Datenbankfehler
from .forms import MovieForm, ContactForm # <--- STELL SICHER, DASS DIESE ZEILE DA IST UND ContactForm ENTHÄLT
from .models import Movie, ContactMessage # <--- UND DIESE ZEILE MIT BEIDEN MODELS

def wishlist_view(request):
    movies = Movie.objects.all()
    form = MovieForm()
    context = {'form': form, 'movies': movies}
    return render(request, 'wishlist.html', context)

def add_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            year = form.cleaned_data['year']

            # Überprüfen, ob der Film bereits existiert
            # case__iexact für case-insensitive Vergleich des Titels
            if Movie.objects.filter(title__iexact=title, year=year).exists():
                messages.error(request, 'This movie is already on the wishlist.')
                return redirect('webapp:wishlist')

            try:
                # Neuen Film erstellen und speichern (likes und added_date werden vom Model gesetzt)
                new_movie = form.save(commit=False) # Speichert nicht sofort, damit wir unique_id etc. behandeln können
                # unique_id und added_date werden automatisch vom Model gesetzt (siehe save-Methode und default=uuid.uuid4)
                new_movie.save() # Jetzt speichern, nachdem alle automatischen Felder gesetzt sind
                
                messages.success(request, f'Movie "{new_movie.title}" added successfully!')
            except IntegrityError: # Fängt falls unique_id aus irgendeinem Grund doch schon existiert
                messages.error(request, 'A database error occurred. Could not add movie due to a unique constraint.')
            except Exception as e:
                # Fängt andere Datenbankfehler ab
                print(f"Error adding movie to DB: {e}")
                messages.error(request, 'Error adding movie. Please try again later.')
            
            return redirect('webapp:wishlist')
        else:
            # Formular ist nicht gültig, zeige Fehler an
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, error)
            return redirect('webapp:wishlist') # Redirect, um Fehler zu zeigen
    return HttpResponseBadRequest("Invalid request method.")


def delete_movie(request, movie_id):
    if request.method == 'POST':
        try:
            # Den Film über seine unique_id abrufen und löschen
            movie = get_object_or_404(Movie, unique_id=movie_id)
            movie_title = movie.title # Titel für die Erfolgsmeldung speichern
            movie.delete()
            messages.success(request, f'Movie "{movie_title}" deleted successfully!')
        except Exception as e:
            print(f"Error deleting movie from DB: {e}")
            messages.error(request, 'Error deleting movie or movie not found.')
        
        return redirect('webapp:wishlist')
    return HttpResponseBadRequest("Invalid request method.")

def like_movie(request, movie_id):
    if request.method == 'POST':
        try:
            # Den Film über seine unique_id abrufen
            movie = get_object_or_404(Movie, unique_id=movie_id)
            movie.likes += 1 # Like erhöhen
            movie.save() # Änderungen speichern
            messages.success(request, f'Movie "{movie.title}" liked successfully! Likes: {movie.likes}')
        except Exception as e:
            print(f"Error liking movie in DB: {e}")
            messages.error(request, 'Error liking movie or movie not found.')
        
        return redirect('webapp:wishlist')
    return HttpResponseBadRequest("Invalid request method.")


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Speichert die Daten des Formulars direkt in der Datenbank
                form.save()
                messages.success(request, 'Your message has been sent successfully!')
                # Leite nach dem Erfolg um, um ein erneutes Senden beim Neuladen zu verhindern (Post/Redirect/Get-Pattern)
                return redirect('webapp:contact') 
            except Exception as e:
                print(f"Error saving contact message to DB: {e}")
                messages.error(request, 'There was an error sending your message. Please try again later.')
        else:
            # Formular ist nicht gültig, Fehler hinzufügen
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, error)
            # Das Formular wird erneut mit den Fehlern gerendert
    else:
        form = ContactForm() # Erstellt ein leeres Formular für GET-Anfragen
    
    context = {'form': form}
    return render(request, 'contact.html', context)
