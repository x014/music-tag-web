import base64
import copy
import copy
import datetime
import os
import time
import uuid

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from rest_framework import mixins
from rest_framework.decorators import action

from applications.task.constants import ALLOW_TYPE
from applications.task.filters import TaskFilters
from applications.task.models import TaskRecord, Task, BatchTask
from applications.task.serialziers import FileListSerializer, Id3Serializer, UpdateId3Serializer, \
    FetchId3ByTitleSerializer, FetchLlyricSerializer, BatchUpdateId3Serializer, TranslationLycSerializer, \
    TidyFolderSerializer, TaskSerializer, UploadImageSerializer, BatchTaskSerializer
from applications.task.services.music_ids import MusicIDS
from applications.task.services.music_resource import MusicResource
from applications.task.services.update_ids import update_music_info
from applications.task.tasks import full_scan_folder, scan, clear_music, batch_auto_tag_task, tidy_folder_task
from applications.utils.translation import translation_lyc_text
from component.drf.viewsets import GenericViewSet
from django_vue_cli.celery_app import app as celery_app


@method_decorator(gzip_page, name="dispatch")
class TaskViewSets(GenericViewSet):
    def get_serializer_class(self):
        if self.action == "file_list":
            return FileListSerializer
        elif self.action == "music_id3":
            return Id3Serializer
        elif self.action == "update_id3":
            return UpdateId3Serializer
        elif self.action == "fetch_id3_by_title":
            return FetchId3ByTitleSerializer
        elif self.action == "fetch_lyric":
            return FetchLlyricSerializer
        elif self.action in ["batch_update_id3", "batch_auto_update_id3"]:
            return BatchUpdateId3Serializer
        elif self.action == "translation_lyc":
            return TranslationLycSerializer
        elif self.action == "tidy_folder":
            return TidyFolderSerializer
        elif self.action == "upload_image":
            return UploadImageSerializer
        return FileListSerializer

    @action(methods=['POST'], detail=False)
    def file_list(self, request, *args, **kwargs):
        """文件列表"""
        validate_data = self.is_validated_data(request.data)
        file_path = validate_data['file_path']
        sorted_fields = validate_data['sorted_fields']
        file_path_list = file_path.split('/')
        
        # 路径转换：将 /app/media/ 转换为实际的 MEDIA_ROOT 路径
        if file_path.startswith('/app/media/'):
            file_path = file_path.replace('/app/media/', settings.MEDIA_ROOT + os.sep)
        elif file_path == '/app/media/' or file_path == '/app/media':
            file_path = settings.MEDIA_ROOT
        
        try:
            data = os.scandir(file_path)
        except FileNotFoundError:
            return self.failure_response(msg="文件夹不存在")
        children_data = []
        frc_map = {}
        file_data = []
        full_path_list = []
        for entry in data:
            each = entry.name.encode('utf-8', 'replace').decode()
            file_data.append({
                "name": each,
                "path": entry.path.encode('utf-8', 'replace').decode(),
                "is_dir": entry.is_dir(),
                "update_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry.stat().st_mtime)),
                "size": entry.stat().st_size
            })
            full_path_list.append(f"{file_path}/{each}")
            file_type = each.split(".")[-1]
            file_name = ".".join(each.split(".")[:-1])
            if file_type in ["lrc", "txt"]:
                frc_map[file_name] = each
        task_map = dict(Task.objects.filter(parent_path=file_path).values_list("filename", "state"))
        for index, entry in enumerate(file_data, 1):
            each = entry.get("name")
            file_type = each.split(".")[-1]
            file_name = ".".join(each.split(".")[:-1])
            if entry.get("is_dir", None):
                children_data.append({
                    "id": index,
                    "name": each,
                    "title": each,
                    "icon": "icon-folder",
                    "state": "null",
                    "children": [],
                    "size": entry.get("size"),
                    "update_time": entry.get("update_time")
                })
                continue
            if file_type not in ALLOW_TYPE:
                continue
            if file_name in frc_map:
                icon = "icon-script-files"
            else:
                icon = "icon-script-file"
            children_data.append({
                "id": index,
                "name": each,
                "title": each,
                "icon": icon,
                "state": task_map.get(each, "null"),
                "size": entry.get("size"),
                "update_time": entry.get("update_time")
            })
        if "name" in sorted_fields:
            children_data = sorted(children_data, key=lambda x: x.get("name").encode('gbk', "ignore"), reverse=False)
        if "update_time" in sorted_fields:
            children_data = sorted(children_data, key=lambda x: x.get("update_time"), reverse=True)
        if "size" in sorted_fields:
            children_data = sorted(children_data, key=lambda x: x.get("size"), reverse=True)
        res_data = [
            {
                "name": file_path_list[-1],
                "title": file_path_list[-1],
                "expanded": True,
                "id": 0,
                "children": children_data,
                "icon": "icon-folder",
            }
        ]
        return self.success_response(data=res_data)

    @action(methods=['POST'], detail=False)
    def music_id3(self, request, *args, **kwargs):
        """获取音乐id3信息"""
        validate_data = self.is_validated_data(request.data)
        file_path = validate_data['file_path']
        file_name = validate_data['file_name']
        file_type = file_name.split(".")[-1]
        if file_type in ["lrc", "txt"]:
            return self.success_response()
        
        # 路径转换：将 /app/media/ 转换为实际的 MEDIA_ROOT 路径
        if file_path.startswith('/app/media/'):
            file_path = file_path.replace('/app/media/', settings.MEDIA_ROOT + os.sep)
        elif file_path == '/app/media/' or file_path == '/app/media':
            file_path = settings.MEDIA_ROOT
        
        file_path = file_path.rstrip('/')
        sub_path = file_path.split('/')[-1]
        if sub_path == file_name:
            return self.success_response()
        try:
            res_data = MusicIDS(f"{file_path}/{file_name}").to_dict()
        except Exception as e:
            return self.failure_response(msg=str(e))
        return self.success_response(data=res_data)

    @action(methods=['POST'], detail=False)
    def update_id3(self, request, *args, **kwargs):
        """更新音乐id3信息"""
        validate_data = self.is_validated_data(request.data)
        music_id3_info = validate_data['music_id3_info']
        update_music_info(music_id3_info, False)
        return self.success_response()

    @action(methods=['POST'], detail=False)
    def batch_update_id3(self, request, *args, **kwargs):
        """批量更新音乐id3信息"""
        validate_data = self.is_validated_data(request.data)
        full_path = validate_data['file_full_path']
        
        # 路径转换：将 /app/media/ 转换为实际的 MEDIA_ROOT 路径
        if full_path.startswith('/app/media/'):
            full_path = full_path.replace('/app/media/', settings.MEDIA_ROOT + os.sep)
        elif full_path == '/app/media/' or full_path == '/app/media':
            full_path = settings.MEDIA_ROOT
        
        select_data = validate_data['select_data']
        music_info = validate_data['music_info']
        music_id3_info = []
        for data in select_data:
            if data.get('icon') == 'icon-folder':
                file_full_path = f"{full_path}/{data.get('name')}"
                data = os.scandir(file_full_path)
                allow_type = ["flac", "mp3", "ape", "wav", "aiff", "wv", "tta", "m4a", "ogg", "mpc",
                              "opus", "wma", "dsf", "dff"]
                for index, entry in enumerate(data, 1):
                    each = entry.name
                    file_type = each.split(".")[-1]
                    if file_type not in allow_type:
                        continue
                    music_info.update({
                        "file_full_path": f"{file_full_path}/{each}",
                        "filename": each
                    })
                    music_id3_info.append(copy.deepcopy(music_info))
            else:
                music_info.update({
                    "file_full_path": f"{full_path}/{data.get('name')}",
                })
                music_id3_info.append(copy.deepcopy(music_info))
        update_music_info(music_id3_info, False)
        return self.success_response()

    @action(methods=['POST'], detail=False)
    def batch_auto_update_id3(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        full_path = validate_data['file_full_path']
        
        if full_path.startswith('/app/media/'):
            full_path = full_path.replace('/app/media/', settings.MEDIA_ROOT + os.sep)
        elif full_path == '/app/media/' or full_path == '/app/media':
            full_path = settings.MEDIA_ROOT
        
        select_data = validate_data['select_data']
        music_info = validate_data['music_info']
        select_mode = music_info.get("select_mode", "hard")
        source_list = music_info.get("source_list", [])
        
        batch_id = str(uuid.uuid4())
        
        batch_task = BatchTask.objects.create(
            batch_id=batch_id,
            task_type='auto_tag',
            status='pending'
        )
        
        bulk_set = []
        for each in select_data:
            name = each.get("name")
            song_name = ".".join(name.split(".")[:-1])
            bulk_set.append(TaskRecord(**{
                "song_name": song_name,
                "full_path": f"{full_path}/{name}",
                "icon": each.get("icon"),
                "batch": batch_id
            }))
        TaskRecord.objects.bulk_create(bulk_set, batch_size=500)
        
        batch_auto_tag_task.delay(batch_id, source_list, select_mode)
        
        return self.success_response(data={
            "batch_id": batch_id,
            "message": "任务已创建，正在后台执行"
        })

    @action(methods=['POST'], detail=False)
    def fetch_lyric(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        resource = validate_data["resource"]
        song_id = validate_data["song_id"]
        try:
            lyric = MusicResource(resource).fetch_lyric(song_id) or ""
        except Exception as e:
            lyric = f"未找到歌词 {e}"
        return self.success_response(data=lyric)

    @action(methods=['POST'], detail=False)
    def fetch_id3_by_title(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        resource = validate_data["resource"]
        full_path = validate_data.get("full_path", "")
        title = validate_data["title"]

        if resource == "acoustid":
            title = full_path
        elif resource == "smart_tag":
            title = {"title": title, "full_path": full_path}
        songs = MusicResource(resource).fetch_id3_by_title(title)
        return self.success_response(data=songs)

    @action(methods=['POST'], detail=False)
    def translation_lyc(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        lyc = validate_data["lyc"]
        clean_lyc_list = []
        raw_lyc_list = []
        for line in lyc.split("\n"):
            if not line:
                continue
            clean_line = line.split("]")[-1]
            clean_line = clean_line.strip()
            if not clean_line:
                continue
            raw_lyc_list.append(line)
            clean_lyc_list.append(clean_line)
        clean_lyc_str = "\n".join(clean_lyc_list)
        results = translation_lyc_text(clean_lyc_str)
        new_lyc = []
        results_list = results.split("\n")
        for index, result in enumerate(results_list):
            if not result:
                new_lyc.append(raw_lyc_list[index])
            else:
                try:
                    src = clean_lyc_list[index]
                    raw_src = raw_lyc_list[index]
                except Exception as e:
                    continue
                if src.replace(" ", "") == result.replace(" ", ""):
                    new_lyc.append(raw_src)
                else:
                    new_lyc.append(f"{raw_src}\n「{result}」\n")
        return self.success_response(data="\n".join(new_lyc))

    @action(methods=['POST'], detail=False)
    def tidy_folder(self, request, *args, **kwargs):
        validate_data = self.is_validated_data(request.data)
        root_path = validate_data["root_path"]
        first_dir = validate_data["first_dir"]
        full_path = validate_data["file_full_path"]
        
        if full_path.startswith('/app/media/'):
            full_path = full_path.replace('/app/media/', settings.MEDIA_ROOT + os.sep)
        elif full_path == '/app/media/' or full_path == '/app/media':
            full_path = settings.MEDIA_ROOT
        
        if root_path.startswith('/app/media/'):
            root_path = root_path.replace('/app/media/', settings.MEDIA_ROOT + os.sep)
        elif root_path == '/app/media/' or root_path == '/app/media':
            root_path = settings.MEDIA_ROOT
        
        select_data = validate_data["select_data"]
        second_dir = validate_data.get("second_dir", "")
        music_id3_info = []
        for data in select_data:
            if data.get('icon') == 'icon-folder':
                file_full_path = f"{full_path}/{data.get('name')}"
                data = os.scandir(file_full_path)
                for index, entry in enumerate(data, 1):
                    each = entry.name
                    file_type = each.split(".")[-1]
                    if file_type not in ALLOW_TYPE:
                        continue
                    music_id3_info.append(f"{file_full_path}/{each}")
            else:
                music_id3_info.append(f"{full_path}/{data.get('name')}")
        
        batch_id = str(uuid.uuid4())
        
        BatchTask.objects.create(
            batch_id=batch_id,
            task_type='tidy_folder',
            status='pending',
            total_count=len(music_id3_info)
        )
        
        tidy_folder_task.delay(batch_id, music_id3_info, {
            "root_path": root_path, 
            "first_dir": first_dir, 
            "second_dir": second_dir
        })
        
        return self.success_response(data={
            "batch_id": batch_id,
            "message": "整理任务已创建，正在后台执行"
        })

    @action(methods=['POST'], detail=False)
    def upload_image(self, request, *args, **kwargs):
        upload_file = request.FILES.get('upload_file')

        bs64_img = base64.b64encode(upload_file.read()).decode()
        # bs64_img_str = "data:image/jpeg;base64," + bs64_img
        return self.success_response(data=bs64_img)

    @action(methods=["get"], detail=False)
    def clear_celery(self, request, *args, **kwargs):
        active_tasks = celery_app.control.inspect().active()
        try:
            active_tasks_data = list(active_tasks.values())[0]
        except Exception:
            return self.success_response()
        for task in active_tasks_data:
            celery_app.control.revoke(task["id"], terminate=True)
        celery_app.control.purge()
        return self.success_response()

    @action(methods=["get"], detail=False)
    def active_queue(self, request, *args, **kwargs):
        active_tasks = celery_app.control.inspect().active()
        try:
            active_tasks_data = list(active_tasks.values())[0]
        except Exception:
            return self.success_response()
        return self.success_response(data=active_tasks_data)

    @action(methods=['GET'], detail=False)
    def task1(self, request, *args, **kwargs):
        scan.delay()
        return self.success_response()

    @action(methods=['GET'], detail=False)
    def task2(self, request, *args, **kwargs):
        clear_music()
        return self.success_response()

    @action(methods=['GET'], detail=False)
    def full_scan_folder(self, request, *args, **kwargs):
        full_scan_folder.delay()
        return self.success_response()

    @action(methods=['GET'], detail=False)
    def batch_progress(self, request, *args, **kwargs):
        """查询批量任务进度"""
        batch_id = request.query_params.get('batch_id')
        if not batch_id:
            return self.failure_response(msg="缺少 batch_id 参数")
        
        batch_task = BatchTask.objects.filter(batch_id=batch_id).first()
        if not batch_task:
            return self.failure_response(msg="任务不存在")
        
        return self.success_response(data={
            "batch_id": batch_task.batch_id,
            "task_type": batch_task.task_type,
            "status": batch_task.status,
            "total_count": batch_task.total_count,
            "success_count": batch_task.success_count,
            "failed_count": batch_task.failed_count,
            "current_index": batch_task.current_index,
            "progress_percent": batch_task.progress_percent,
            "progress_text": batch_task.progress_text,
            "error_message": batch_task.error_message,
            "created_at": batch_task.created_at,
            "started_at": batch_task.started_at,
            "finished_at": batch_task.finished_at,
        })

    @action(methods=['GET'], detail=False)
    def batch_list(self, request, *args, **kwargs):
        """获取批量任务列表"""
        task_type = request.query_params.get('task_type')
        status = request.query_params.get('status')
        
        queryset = BatchTask.objects.all()
        if task_type:
            queryset = queryset.filter(task_type=task_type)
        if status:
            queryset = queryset.filter(status=status)
        
        queryset = queryset[:20]
        
        data = []
        for batch in queryset:
            data.append({
                "batch_id": batch.batch_id,
                "task_type": batch.task_type,
                "status": batch.status,
                "total_count": batch.total_count,
                "success_count": batch.success_count,
                "failed_count": batch.failed_count,
                "progress_percent": batch.progress_percent,
                "created_at": batch.created_at,
                "finished_at": batch.finished_at,
            })
        
        return self.success_response(data=data)

    @action(methods=['POST'], detail=False)
    def batch_cancel(self, request, *args, **kwargs):
        """取消批量任务"""
        batch_id = request.data.get('batch_id')
        if not batch_id:
            return self.failure_response(msg="缺少 batch_id 参数")
        
        batch_task = BatchTask.objects.filter(batch_id=batch_id).first()
        if not batch_task:
            return self.failure_response(msg="任务不存在")
        
        if batch_task.status in ['completed', 'failed', 'cancelled']:
            return self.failure_response(msg="任务已结束，无法取消")
        
        batch_task.status = 'cancelled'
        batch_task.finished_at = datetime.datetime.now()
        batch_task.save()
        
        return self.success_response(msg="任务已取消")

    @action(methods=['GET'], detail=False)
    def batch_records(self, request, *args, **kwargs):
        """获取批量任务的详细记录"""
        batch_id = request.query_params.get('batch_id')
        state = request.query_params.get('state')
        
        if not batch_id:
            return self.failure_response(msg="缺少 batch_id 参数")
        
        queryset = TaskRecord.objects.filter(batch=batch_id)
        if state:
            queryset = queryset.filter(state=state)
        
        queryset = queryset[:100]
        
        data = []
        for record in queryset:
            data.append({
                "id": record.id,
                "song_name": record.song_name,
                "artist_name": record.artist_name,
                "full_path": record.full_path,
                "state": record.state,
                "match_source": record.match_source,
                "match_score": record.match_score,
                "error_message": record.error_message,
                "process_time": round(record.process_time, 2),
            })
        
        return self.success_response(data=data)


class TaskModelViewSets(mixins.ListModelMixin,
                        GenericViewSet):
    queryset = Task.objects.order_by("-id")
    serializer_class = TaskSerializer
    filterset_class = TaskFilters
