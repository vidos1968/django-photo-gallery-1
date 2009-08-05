"""
views for albums
"""

from django.views.generic.list_detail import object_list
from netwizard.photogallery.models import Photo, Album

def list(request, queryset=None, template_name=None, **kwargs):
    queryset = queryset or Album.objects.published() 
    return object_list(request, paginate_by=50,
            queryset=queryset,
            template_name='photogallery/list_albums.html' or template_name,
            template_object_name='album')

def index(request, **kwargs):
    return list(request, **kwargs)
