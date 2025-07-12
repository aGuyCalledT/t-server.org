from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse # Import hinzugefügt für Fehlerfälle
from .forms import ContactForm, MovieForm
import os
import csv
from datetime import datetime

# Pfad zur CSV-Datei definieren
CSV_FILE_PATH = os.path.join(settings.BASE_DIR, 'movies.csv')

def read_movies_from_csv():
    movies = []
    # Prüfen, ob die Datei existiert und nicht leer ist.
    if not os.path.exists(CSV_FILE_PATH) or os.path.getsize(CSV_FILE_PATH) == 0:
        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['title', 'year', 'likes', 'added_date'])
        return []

    with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as csvfile:
        try:
            reader = csv.DictReader(csvfile)
            # Überprüfen, ob die erwarteten Spaltennamen vorhanden sind
            expected_fieldnames = ['title', 'year', 'likes', 'added_date']
            if not reader.fieldnames or not all(f in reader.fieldnames for f in expected_fieldnames):
                print(f"Warning: CSV file '{CSV_FILE_PATH}' has missing or incorrect headers. Recreating file with correct headers.")
                with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as new_csvfile: # Hier wurde 'utf-analysis' zu 'utf-8' geändert
                    writer = csv.writer(new_csvfile)
                    writer.writerow(expected_fieldnames)
                return []
            
            for row in reader:
                if all(key in row for key in expected_fieldnames):
                    try:
                        likes = int(row.get('likes', 0))
                    except ValueError:
                        likes = 0 # Fallback falls 'likes' keine Zahl ist

                    added_date_display = ''
                    if row.get('added_date'):
                        try:
                            # Parse das Datum im YYYY-MM-DD Format
                            parsed_added_date = datetime.strptime(row['added_date'], '%Y-%m-%d').date()
                            # Für die Anzeige auf der Webseite in "Sat. 12.07.2025" Format formatieren
                            added_date_display = parsed_added_date.strftime('%a. %d.%m.%Y')
                        except ValueError:
                            added_date_display = row['added_date'] # Zeige es so an, wie es ist
                            
                    movies.append({
                        'title': row['title'],
                        'year': row.get('year', ''),
                        'likes': likes,
                        'added_date': added_date_display,
                    })
                else:
                    print(f"Warning: Skipping malformed row in CSV: {row}")

        except csv.Error as e:
            print(f"Error reading CSV file '{CSV_FILE_PATH}': {e}. Recreating empty file.")
            with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['title', 'year', 'likes', 'added_date'])
            return []
            
    return movies

def write_movies_to_csv(movies_data):
    # Diese Funktion schreibt die komplette Liste der Filme neu in die CSV
    with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'year', 'likes', 'added_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(movies_data)


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            contacts_file_path = os.path.join(settings.BASE_DIR, 'contacts.txt')

            try:
                with open(contacts_file_path, 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"--- Contact Entry ({timestamp}) ---\n")
                    f.write(f"Name: {name}\n")
                    f.write(f"Email: {email}\n")
                    f.write(f"Message:\n{message}\n\n")
                return redirect('webapp:contact_success')
            except IOError as e:
                print(f"Error writing to contacts.txt: {e}")
                return HttpResponse("Error saving message. Please try again.", status=500)

    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

def contact_success_view(request):
    return render(request, 'contact_success.html')

def wishlist_view(request):
    movies = read_movies_from_csv() # Immer die aktuelle Liste lesen

    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title'].strip() # Leerzeichen entfernen
            year = form.cleaned_data['year'].strip() # Leerzeichen entfernen
            
            # Prüfen, ob der Film bereits existiert
            movie_exists = False
            for movie in movies:
                if movie['title'].lower() == title.lower(): # Case-insensitive Vergleich
                    movie['likes'] += 1 # Bestehenden Film liken
                    movie_exists = True
                    break
            
            if not movie_exists:
                # Neuen Film hinzufügen
                current_date = datetime.now().strftime('%Y-%m-%d')
                new_movie = {
                    'title': title,
                    'year': year,
                    'likes': 0, # Neue Filme starten mit 0 Likes
                    'added_date': current_date # Datum des Hinzufügens speichern
                }
                movies.append(new_movie)
            
            # Sortiere die Filme nach Likes (absteigend) und dann nach Titel (aufsteigend)
            movies.sort(key=lambda x: (x['likes'], x['title']), reverse=True)
            
            try:
                write_movies_to_csv(movies) # Gesamte (aktualisierte) Liste neu schreiben
                return redirect('webapp:wishlist') # Seite neu laden, um Änderungen zu sehen
            except IOError as e:
                print(f"Error writing to movies.csv: {e}")
                return HttpResponse("Error adding movie. Please try again.", status=500)
    else:
        form = MovieForm()
    
    # Sortiere die Filme auch beim initialen Laden nach Likes
    movies.sort(key=lambda x: (x['likes'], x['title']), reverse=True)

    return render(request, 'wishlist.html', {'form': form, 'movies': movies})

def like_movie(request, movie_index):
    if request.method == 'POST':
        movies = read_movies_from_csv()
        if 0 <= movie_index < len(movies):
            movies[movie_index]['likes'] += 1
            # Sortiere die Liste neu nach dem Liken
            movies.sort(key=lambda x: (x['likes'], x['title']), reverse=True)
            try:
                write_movies_to_csv(movies)
                return redirect('webapp:wishlist')
            except IOError as e:
                print(f"Error writing to movies.csv: {e}")
                return HttpResponse("Error liking movie. Please try again.", status=500)
        else:
            return HttpResponse("Movie not found.", status=404)
    return redirect('webapp:wishlist') # Immer zur Wunschliste zurückleiten, auch bei GET
