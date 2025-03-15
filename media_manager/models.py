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
        is_new = self.pk is None
        if is_new and self.media_type == 'video' and self.file:
            try:
                # 一時ファイルとして動画を保存
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(self.file.name)[1]) as temp_file:
                    for chunk in self.file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name

                try:
                    # 動画の最初のフレームを取得
                    cap = cv2.VideoCapture(temp_file_path)
                    if not cap.isOpened():
                        raise Exception("動画ファイルを開けませんでした")
                    
                    ret, frame = cap.read()
                    if not ret:
                        raise Exception("動画からフレームを取得できませんでした")
                    
                    cap.release()

                    # OpenCVのBGRからRGBに変換
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # PILイメージに変換
                    pil_image = Image.fromarray(rgb_frame)
                    
                    # サイズを調整（最大幅500px）
                    max_size = 500
                    ratio = min(max_size/float(pil_image.size[0]), max_size/float(pil_image.size[1]))
                    new_size = tuple([int(x*ratio) for x in pil_image.size])
                    pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # バッファにJPEGとして保存
                    buffer = io.BytesIO()
                    pil_image.save(buffer, format='JPEG', quality=85)
                    
                    # ContentFileとしてサムネイルに保存
                    file_name = f"{os.path.splitext(self.file.name)[0]}_thumb.jpg"
                    self.thumbnail.save(file_name, ContentFile(buffer.getvalue()), save=False)
                finally:
                    # 一時ファイルを削除
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
            except Exception as e:
                print(f"サムネイル生成エラー: {e}")
                # エラーが発生した場合でも、モデルは保存できるようにする
                self.thumbnail = None

        super().save(*args, **kwargs)
