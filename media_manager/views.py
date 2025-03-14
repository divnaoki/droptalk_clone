from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import MediaItem
from .forms import MediaItemForm

def media_list(request):
    media_items = MediaItem.objects.all()
    return render(request, 'media_manager/media_list.html', {'media_items': media_items})

@login_required
def media_upload(request):
    if request.method == 'POST':
        form = MediaItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'メディアをアップロードしました。')
            return redirect('media_manager:media_list')
    else:
        form = MediaItemForm()
    return render(request, 'media_manager/media_upload.html', {'form': form})

@login_required
def media_edit(request, pk):
    media_item = get_object_or_404(MediaItem, pk=pk)
    if request.method == 'POST':
        form = MediaItemForm(request.POST, request.FILES, instance=media_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'メディアを更新しました。')
            return redirect('media_manager:media_list')
    else:
        form = MediaItemForm(instance=media_item)
    return render(request, 'media_manager/media_edit.html', {'form': form, 'media_item': media_item})

@login_required
def media_delete(request, pk):
    media_item = get_object_or_404(MediaItem, pk=pk)
    if request.method == 'POST':
        media_item.delete()
        messages.success(request, 'メディアを削除しました。')
        return redirect('media_manager:media_list')
    return render(request, 'media_manager/media_delete.html', {'media_item': media_item})

def media_detail(request, pk):
    media_item = get_object_or_404(MediaItem, pk=pk)
    return render(request, 'media_manager/media_detail.html', {'media_item': media_item})
