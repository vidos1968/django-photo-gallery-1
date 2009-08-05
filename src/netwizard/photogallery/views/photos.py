from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_page
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from netwizard.django.helpers import flash, redirect
from tagging.views import tagged_object_list

from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import update_object, create_object

from netwizard.photogallery.models import Photo, Album
from netwizard.photogallery import forms, auth




def list(request, id=None, slug=None, template_name=None, paginate_by=None, **kwargs):
    photos = Photo.objects.published()
    album = None
    if id: # album
        photos = photos.filter(album=id)
        album = Album.objects.published().get(id=id)
    elif slug:
        album = Album.objects.published().get(slug=slug)
        photos = album.photos.published()

    ctx = {
        'album': album,
        'last_updated_at': Photo.objects.get_max_updated_at(photos),
        'tag': None,
        }

    return object_list(request, paginate_by=paginate_by or 25,
            queryset=photos, template_name=template_name or 'photogallery/list.html',
            extra_context=ctx, template_object_name='photo', **kwargs)


def list_tagged(request, tag, template_name=None, extra_context=None, paginate_by=None, **kwargs):
    photos = Photo.objects.published()
    ctx = extra_context or {}
    ctx.update({
        'last_updated_at': Photo.objects.get_max_updated_at(photos),
        'tag': tag,
        })
    return tagged_object_list(request, tag=tag, paginate_by=paginate_by or 25,
            queryset_or_model=photos, template_name=template_name or 'photogallery/list.html',
            extra_context=ctx, template_object_name='photo', **kwargs)


def show(request, id, template_name=None, extra_context=None, **kw):
    return object_detail(request, object_id=id,
            queryset=Photo.objects.published(),
            template_name=template_name or 'photogallery/show.html',
            extra_context = extra_context,
            template_object_name='photo', **kw)


@login_required
@never_cache
def edit(request, id, form_class=forms.PhotoEdit, redirect_to=None, template_name=None):
    try:
        photo = Photo.objects.published().get(id=id)
        if not auth.can_edit_photo(request.user, photo):
            raise Photo.DoesNotExist
    except Photo.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            photo = form.save(commit=False)
            if request.POST.get('create_album'):
                album = Album()
                album.title = request.POST.get('new_album_name')
                self.flash(_('Album %(name)s created') % {'name': album.title })
                album.save()
                photo.album = album
            if photo.album:
                photo.album.updated_at = datetime.datetime.now()
                photo.album.save(force_update=True)
            photo.save()
            flash(request, _('Photo updated') if id else _('Photo added'))
            return redirect(reverse='photogallery-photos-show', id=photo.id)
    else:
        form = forms.form_class(instance=photo)

    ctx = extra_context or {}
    ctx.update({'form': form, 'photo': photo, 'can_edit': can_edit})

    return render_to_response(template_name or 'photogallery/edit_photo.html',
            ctx, RequestContext(request))
