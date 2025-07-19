from django.contrib import admin
from .models import Movie, ContactMessage # Importiere deine Models

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # Optionen für die Anzeige in der Liste
    list_display = ('title', 'year', 'likes', 'added_date', 'unique_id')
    # Filter-Optionen in der Seitenleiste
    list_filter = ('year', 'added_date')
    # Suchfeld
    search_fields = ('title', 'year')
    # Felder, die nur lesbar sind (nicht direkt bearbeitbar im Admin)
    readonly_fields = ('unique_id', 'added_date')
    # Sortierung (falls nicht schon im Model über Meta.ordering definiert)
    # ordering = ('-added_date',) # Kann hier überschrieben werden
    
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    # Welche Felder in der Übersicht angezeigt werden sollen
    list_display = ('name', 'email', 'timestamp', 'message_snippet')
    # Filter
    list_filter = ('timestamp',)
    # Suchfeld
    search_fields = ('name', 'email', 'message')
    # Felder, die nur lesbar sind
    readonly_fields = ('timestamp',)

    # Eine Methode, um eine gekürzte Nachrichten-Vorschau anzuzeigen
    def message_snippet(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_snippet.short_description = 'Message Preview' # Spaltenüberschrift
