from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import FilmWork  # Updated from Filmwork

class MoviesApiMixin:
    model = FilmWork  # Updated from Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        results = FilmWork.objects.prefetch_related(
            'genres',
            'persons'
        ).values(
            'id',
            'title',
            'description',
            'creation_date',
            'rating',
            'type'
        ).annotate(
            genres=ArrayAgg('genres__genre__name', distinct=True),
            actors=ArrayAgg(
                'persons__person__full_name',
                filter=Q(persons__role='actor'),
                distinct=True
            ),
            directors=ArrayAgg(
                'persons__person__full_name',
                filter=Q(persons__role='director'),
                distinct=True
            ),
            writers=ArrayAgg(
                'persons__person__full_name',
                filter=Q(persons__role='writer'),
                distinct=True
            )
        )
        return results

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)

class MoviesListApi(MoviesApiMixin, BaseListView):
    def get_context_data(self, *, object_list=None, **kwargs):
        self.paginate_by = 50
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )
        return {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(queryset)
        }

class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        return self.get_object(queryset)
