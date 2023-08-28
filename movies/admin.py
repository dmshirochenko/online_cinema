from django.contrib import admin
from .models import Genre, FilmWork, GenreFilmWork, Person, PersonFilmWork  # Corrected model names

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name",)

class GenreFilmWorkInline(admin.TabularInline):  # Corrected class name
    model = GenreFilmWork  # Corrected model name
    autocomplete_fields = ("genre",)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass

class PersonFilmWorkInline(admin.TabularInline):  # Corrected class name
    model = PersonFilmWork  # Corrected model name

@admin.register(FilmWork)  # Corrected model name
class FilmWorkAdmin(admin.ModelAdmin):  # Corrected class name
    inlines = (
        GenreFilmWorkInline,  # Corrected class name
        PersonFilmWorkInline,  # Corrected class name
    )
    
    list_display = ("title", "type", "get_genres", "rating", "creation_date")
    list_filter = ("type",)
    search_fields = ("title", "description", "id")
    
    # Prefetching corrected based on your model relationships
    list_prefetch_related = ("genrefilmwork_set__genre", "personfilmwork_set__person")

    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related(*self.list_prefetch_related)
        return queryset

    def get_genres(self, obj):
        return ", ".join([str(genre.genre.name) for genre in obj.genrefilmwork_set.all()])  # Adjusted based on model relationships

    get_genres.short_description = "Film Genre"
