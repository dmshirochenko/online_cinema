from django.db import models


class FilmWork(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    type = models.TextField()
    file_path = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'film_work'


class Genre(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(unique=True, max_length=64)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'genre'


class GenreFilmWork(models.Model):
    id = models.UUIDField(primary_key=True)
    genre = models.ForeignKey(Genre, models.DO_NOTHING, related_name='film_works')
    film_work = models.ForeignKey(FilmWork, models.DO_NOTHING, related_name='genres')
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'genre_film_work'
        unique_together = (('film_work', 'genre'),)


class Person(models.Model):
    id = models.UUIDField(primary_key=True)
    full_name = models.CharField(unique=True, max_length=64)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'person'


class PersonFilmWork(models.Model):
    id = models.UUIDField(primary_key=True)
    person = models.ForeignKey(Person, models.DO_NOTHING)
    film_work = models.ForeignKey(FilmWork, models.DO_NOTHING, related_name='persons')
    role = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'person_film_work'
        unique_together = (('film_work', 'person', 'role'),)
