from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
import cv2
import numpy as np
from PIL import Image
import io
import tempfile
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class MediaItem(models.Model):
    MEDIA_TYPES = (
        ('image', '画像'),
        ('video', '動画'),
    )
    
    title = models.CharField('タイトル', max_length=200)
    description = models.TextField('説明', blank=True)
    media_type = models.CharField('メディアタイプ', max_length=5, choices=MEDIA_TYPES)
    file = models.FileField('ファイル', upload_to='media/%Y/%m/%d/')
    thumbnail = models.ImageField('サムネイル', upload_to='thumbnails/%Y/%m/%d/', blank=True, null=True)
    created_at = models.DateTimeField('作成日時', default=timezone.now)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'メディアアイテム'
        verbose_name_plural = 'メディアアイテム'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # サムネイル生成機能は一時的に無効化
        super().save(*args, **kwargs)
