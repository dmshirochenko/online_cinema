import uuid
from django.db import models

# Create your models here.
class FilmWork(models.Model):
    created = models.DateTimeField()
    modified = models.DateTimeField()
    id = models.UUIDField(primary_key=True)
    certificate = models.CharField(max_length=512, blank=True, null=True)
    file_path = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateField(unique=True, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    type = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'film_work'


class Genre(models.Model):
    created = models.DateTimeField()
    modified = models.DateTimeField()
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'genre'


class GenreFilmWork(models.Model):
    id = models.UUIDField(primary_key=True)
    film_work = models.ForeignKey(FilmWork, models.DO_NOTHING)
    genre = models.ForeignKey(Genre, models.DO_NOTHING)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'genre_film_work'
        unique_together = (('film_work', 'genre'),)


class Person(models.Model):
    created = models.DateTimeField()
    modified = models.DateTimeField()
    id = models.UUIDField(primary_key=True)
    full_name = models.TextField()

    class Meta:
        managed = False
        db_table = 'person'


class PersonFilmWork(models.Model):
    id = models.UUIDField(primary_key=True)
    role = models.TextField()
    created_at = models.DateTimeField()
    film_work = models.ForeignKey(FilmWork, models.DO_NOTHING)
    person = models.ForeignKey(Person, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'person_film_work'
        unique_together = (('film_work', 'person', 'role'),)