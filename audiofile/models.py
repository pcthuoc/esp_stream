from django.db import models
from django.utils import timezone
from datetime import timedelta

class Audio(models.Model):
    name_file = models.CharField(max_length=100, verbose_name="Tên file")
    date_created = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")
    duration = models.DurationField(verbose_name="Thời lượng",default=timedelta(0))  # Trường mới để lưu thời lượng
    def __str__(self):
        return self.name_file

    class Meta:
        verbose_name = "Audio"
        verbose_name_plural = "Audios"
