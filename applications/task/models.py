from django.db import models


class Task(models.Model):
    song_name = models.CharField(max_length=255, default="")
    artist_name = models.CharField(max_length=255, default="")

    full_path = models.CharField(max_length=255)
    state = models.CharField(max_length=255, default="wait")
    parent_path = models.CharField(max_length=255, default="")
    filename = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(null=True, auto_now_add=True)


class TaskRecord(models.Model):
    song_name = models.CharField(max_length=255, default="")
    artist_name = models.CharField(max_length=255, default="")
    full_path = models.CharField(max_length=255, default="")
    tag_source = models.CharField(max_length=255, default="")
    icon = models.CharField(max_length=255, default="icon-folder")
    state = models.CharField(max_length=255, default="wait")
    extra = models.TextField(default="")
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    batch = models.CharField(max_length=255, default="")
    match_source = models.CharField(max_length=50, default="")
    match_score = models.FloatField(default=0)
    error_message = models.TextField(default="")
    process_time = models.FloatField(default=0)


class BatchTask(models.Model):
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]
    
    TASK_TYPE_CHOICES = [
        ('auto_tag', '自动刮削'),
        ('tidy_folder', '整理文件夹'),
    ]
    
    batch_id = models.CharField(max_length=255, unique=True)
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES, default='auto_tag')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    total_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    current_index = models.IntegerField(default=0)
    error_message = models.TextField(default="")
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def progress_percent(self):
        if self.total_count == 0:
            return 0
        return round((self.current_index / self.total_count) * 100, 1)
    
    @property
    def progress_text(self):
        return f"{self.current_index}/{self.total_count}"
