import pytest
import os
import uuid
from unittest.mock import Mock, patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile

from applications.task.models import Task, TaskRecord, BatchTask
from applications.task.serialziers import (
    FileListSerializer, Id3Serializer, MusicId3Serializer, UpdateId3Serializer,
    FetchId3ByTitleSerializer, FetchLlyricSerializer, TaskSerializer, BatchTaskSerializer
)
from applications.task.utils import (
    timestamp_to_dt, match_score, match_artist, parse_filename, detect_language
)


@pytest.mark.django_db
class TestTaskModel:
    def test_create_task(self):
        task = Task.objects.create(
            song_name="Test Song",
            artist_name="Test Artist",
            full_path="/music/test.mp3",
            state="wait",
            parent_path="/music",
            filename="test.mp3"
        )
        assert task.song_name == "Test Song"
        assert task.artist_name == "Test Artist"
        assert task.full_path == "/music/test.mp3"
        assert task.state == "wait"

    def test_task_default_state(self):
        task = Task.objects.create(full_path="/music/test.mp3")
        assert task.state == "wait"

    def test_task_auto_created_at(self):
        task = Task.objects.create(full_path="/music/test.mp3")
        assert task.created_at is not None


@pytest.mark.django_db
class TestTaskRecordModel:
    def test_create_task_record(self):
        record = TaskRecord.objects.create(
            song_name="Test Song",
            full_path="/music/test.mp3",
            state="wait",
            batch="test-batch-id"
        )
        assert record.song_name == "Test Song"
        assert record.full_path == "/music/test.mp3"
        assert record.state == "wait"
        assert record.batch == "test-batch-id"

    def test_task_record_match_score(self):
        record = TaskRecord.objects.create(
            full_path="/music/test.mp3",
            match_score=0.95
        )
        assert record.match_score == 0.95


@pytest.mark.django_db
class TestBatchTaskModel:
    def test_create_batch_task(self):
        batch_id = str(uuid.uuid4())
        batch = BatchTask.objects.create(
            batch_id=batch_id,
            task_type='auto_tag',
            status='pending',
            total_count=100
        )
        assert batch.batch_id == batch_id
        assert batch.task_type == 'auto_tag'
        assert batch.status == 'pending'
        assert batch.total_count == 100

    def test_progress_percent(self):
        batch = BatchTask.objects.create(
            batch_id=str(uuid.uuid4()),
            total_count=100,
            current_index=50
        )
        assert batch.progress_percent == 50.0

    def test_progress_percent_zero_total(self):
        batch = BatchTask.objects.create(
            batch_id=str(uuid.uuid4()),
            total_count=0,
            current_index=0
        )
        assert batch.progress_percent == 0

    def test_progress_text(self):
        batch = BatchTask.objects.create(
            batch_id=str(uuid.uuid4()),
            total_count=100,
            current_index=50
        )
        assert batch.progress_text == "50/100"

    def test_batch_id_unique(self):
        batch_id = str(uuid.uuid4())
        BatchTask.objects.create(batch_id=batch_id)
        with pytest.raises(Exception):
            BatchTask.objects.create(batch_id=batch_id)

    def test_ordering(self):
        import time
        batch1 = BatchTask.objects.create(batch_id=str(uuid.uuid4()))
        time.sleep(0.01)
        batch2 = BatchTask.objects.create(batch_id=str(uuid.uuid4()))
        batches = list(BatchTask.objects.all())
        assert batches[0].id == batch2.id
        assert batches[1].id == batch1.id


class TestFileListSerializer:
    def test_valid_data(self):
        data = {
            'file_path': '/music/test',
            'sorted_fields': ['name']
        }
        serializer = FileListSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_file_path(self):
        data = {'sorted_fields': ['name']}
        serializer = FileListSerializer(data=data)
        assert not serializer.is_valid()
        assert 'file_path' in serializer.errors

    def test_missing_sorted_fields(self):
        data = {'file_path': '/music/test'}
        serializer = FileListSerializer(data=data)
        assert not serializer.is_valid()
        assert 'sorted_fields' in serializer.errors


class TestId3Serializer:
    def test_valid_data(self):
        data = {
            'file_path': '/music/test',
            'file_name': 'test.mp3'
        }
        serializer = Id3Serializer(data=data)
        assert serializer.is_valid()

    def test_missing_file_name(self):
        data = {'file_path': '/music/test'}
        serializer = Id3Serializer(data=data)
        assert not serializer.is_valid()


class TestMusicId3Serializer:
    def test_valid_data(self):
        data = {
            'title': 'Test Song',
            'artist': 'Test Artist',
            'album': 'Test Album',
            'albumartist': 'Test Album Artist',
            'discnumber': '1',
            'tracknumber': '1',
            'genre': 'Pop',
            'year': '2023',
            'lyrics': 'Test lyrics',
            'is_save_lyrics_file': False,
            'is_save_album_cover': False,
            'comment': '',
            'file_full_path': '/music/test.mp3'
        }
        serializer = MusicId3Serializer(data=data)
        assert serializer.is_valid()

    def test_null_values_allowed(self):
        data = {
            'title': None,
            'artist': None,
            'album': None,
            'albumartist': None,
            'discnumber': None,
            'tracknumber': None,
            'genre': None,
            'year': None,
            'lyrics': None,
            'is_save_lyrics_file': False,
            'is_save_album_cover': False,
            'comment': None,
            'file_full_path': '/music/test.mp3'
        }
        serializer = MusicId3Serializer(data=data)
        assert serializer.is_valid()

    def test_missing_file_full_path(self):
        data = {
            'title': 'Test',
            'artist': 'Artist',
            'album': 'Album',
            'albumartist': '',
            'discnumber': '',
            'tracknumber': '',
            'genre': '',
            'year': '',
            'lyrics': '',
            'is_save_lyrics_file': False,
            'is_save_album_cover': False,
            'comment': ''
        }
        serializer = MusicId3Serializer(data=data)
        assert not serializer.is_valid()


class TestFetchId3ByTitleSerializer:
    def test_valid_data(self):
        data = {
            'title': 'Test Song',
            'resource': 'netease'
        }
        serializer = FetchId3ByTitleSerializer(data=data)
        assert serializer.is_valid()

    def test_optional_full_path(self):
        data = {
            'title': 'Test Song',
            'resource': 'netease',
            'full_path': '/music/test.mp3'
        }
        serializer = FetchId3ByTitleSerializer(data=data)
        assert serializer.is_valid()


class TestFetchLlyricSerializer:
    def test_valid_data(self):
        data = {
            'song_id': '12345',
            'resource': 'netease'
        }
        serializer = FetchLlyricSerializer(data=data)
        assert serializer.is_valid()

    def test_missing_fields(self):
        data = {'song_id': '12345'}
        serializer = FetchLlyricSerializer(data=data)
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestTaskSerializer:
    def test_get_message(self):
        task = Task.objects.create(
            song_name="Test Song",
            full_path="/music/test.mp3"
        )
        serializer = TaskSerializer(task)
        assert "Test Song" in serializer.data['message']

    def test_to_representation_file_exists(self):
        task = Task.objects.create(
            full_path="/nonexistent/path/test.mp3"
        )
        serializer = TaskSerializer(task)
        assert 'is_exists' in serializer.data


@pytest.mark.django_db
class TestBatchTaskSerializer:
    def test_readonly_fields(self):
        batch = BatchTask.objects.create(
            batch_id=str(uuid.uuid4()),
            total_count=100,
            current_index=50
        )
        serializer = BatchTaskSerializer(batch)
        assert 'progress_percent' in serializer.data
        assert 'progress_text' in serializer.data
        assert serializer.data['progress_percent'] == 50.0


class TestTimestampToDt:
    def test_normal_conversion(self):
        timestamp = 1609459200
        result = timestamp_to_dt(timestamp)
        assert result == "2021-01-01 08:00:00"

    def test_custom_format(self):
        timestamp = 1609459200
        result = timestamp_to_dt(timestamp, "%Y-%m-%d")
        assert result == "2021-01-01"


class TestMatchScore:
    def test_exact_match(self):
        result = match_score("test", "test")
        assert result == 2

    def test_contains_match(self):
        result = match_score("test", "test song")
        assert result == 1

    def test_reverse_contains_match(self):
        result = match_score("test song", "test")
        assert result == 1

    def test_no_match(self):
        result = match_score("abc", "xyz")
        assert result == 0

    def test_case_insensitive(self):
        result = match_score("TEST", "test")
        assert result == 2

    def test_space_ignored(self):
        result = match_score("test song", "testsong")
        assert result == 2

    def test_empty_values(self):
        result = match_score("", "test")
        assert result == 0


class TestMatchArtist:
    def test_single_artist(self):
        result = match_artist("Artist1", "Artist1")
        assert result == 2

    def test_multiple_artists(self):
        result = match_artist("Artist1", "Artist1, Artist2")
        assert result >= 2


class TestParseFilename:
    def test_with_number_prefix(self):
        title, artist = parse_filename("3065.光良-童话")
        assert title == "童话"
        assert artist == "光良"

    def test_artist_song_format(self):
        title, artist = parse_filename("李宗盛-山丘")
        assert title == "山丘"
        assert artist == "李宗盛"

    def test_song_only_format(self):
        title, artist = parse_filename("童话")
        assert title == "童话"
        assert artist == ""

    def test_multiple_dashes(self):
        title, artist = parse_filename("artist-song-name")
        assert title == "song-name"
        assert artist == "artist"


class TestDetectLanguage:
    def test_chinese_detection(self):
        result = detect_language("这是一首中文歌曲")
        assert result == "中文"

    def test_english_detection(self):
        result = detect_language("This is an English song")
        assert result == "英文"

    def test_japanese_detection(self):
        result = detect_language("これは日本語の歌です")
        assert result == "日文"

    def test_korean_detection(self):
        result = detect_language("이것은 한국어 노래입니다")
        assert result == "韩文"

    def test_empty_string(self):
        result = detect_language("")
        assert result == "未知"
