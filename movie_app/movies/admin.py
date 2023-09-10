from django.contrib import admin
from .models import Genre, FilmWork, GenreFilmWork, Person, PersonFilmWork

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = ("full_name",)

class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork
    fields = ('custom_genre_name',)  # Custom field 'custom_genre_name'
    readonly_fields = ('custom_genre_name',)  # Make it read-only

    def custom_genre_name(self, instance):
        return instance.genre.name  # Assume name is a field in Genre model

    custom_genre_name.short_description = "Genre Name"  # Column header

class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    fields = ('custom_person_name', 'role', 'created_at')  # Custom field 'custom_person_name'
    readonly_fields = ('custom_person_name',)  # Make it read-only

    def custom_person_name(self, instance):
        return instance.person.full_name  # Assume full_name is a field in Person model

    custom_person_name.short_description = "Person Full Name"  # Column header


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (
        GenreFilmWorkInline,
        PersonFilmWorkInline,
    )

    list_display = ("title", "type", "get_genres", "rating", "creation_date")
    list_filter = ("type",)
    search_fields = ("title", "description", "id")
    list_prefetch_related = ("genres__genre", "persons__person")

    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related(*self.list_prefetch_related)
        return queryset

    def get_genres(self, obj):
        return ", ".join([str(genre.genre.name) for genre in obj.genres.all()])

    get_genres.short_description = "Film Genre"
