from django import forms
from .models import MediaItem
import mimetypes

class MediaItemForm(forms.ModelForm):
    class Meta:
        model = MediaItem
        fields = ['title', 'description', 'media_type', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        media_type = self.cleaned_data.get('media_type')
        
        if file:
            # ファイルの拡張子からMIMEタイプを取得
            content_type, _ = mimetypes.guess_type(file.name)
            
            if media_type == 'image':
                if not content_type or not content_type.startswith('image/'):
                    raise forms.ValidationError('画像ファイルをアップロードしてください。')
            elif media_type == 'video':
                if not content_type or not content_type.startswith('video/'):
                    raise forms.ValidationError('動画ファイルをアップロードしてください。')
            
            if file.size > 50 * 1024 * 1024:  # 50MB
                raise forms.ValidationError('ファイルサイズは50MB以下にしてください。')
        
        return file 