# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0006_auto_20230830_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskrecord',
            name='error_message',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='taskrecord',
            name='match_score',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='taskrecord',
            name='match_source',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='taskrecord',
            name='process_time',
            field=models.FloatField(default=0),
        ),
        migrations.CreateModel(
            name='BatchTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_id', models.CharField(max_length=255, unique=True)),
                ('task_type', models.CharField(choices=[('auto_tag', '自动刮削'), ('tidy_folder', '整理文件夹')], default='auto_tag', max_length=50)),
                ('status', models.CharField(choices=[('pending', '等待中'), ('running', '执行中'), ('completed', '已完成'), ('failed', '失败'), ('cancelled', '已取消')], default='pending', max_length=50)),
                ('total_count', models.IntegerField(default=0)),
                ('success_count', models.IntegerField(default=0)),
                ('failed_count', models.IntegerField(default=0)),
                ('current_index', models.IntegerField(default=0)),
                ('error_message', models.TextField(default='')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
