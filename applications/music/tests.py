import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from applications.music.models import (
    Album, Track, Artist, Genre, Attachment, Playlist, TrackFavorite, Folder
)
from applications.music.validators import ImageDimensionsValidator, FileValidator, DomainValidator
from applications.music.utils import ChunkedPath, strip_absolute_media_url


@pytest.mark.django_db
class TestAlbumModel:
    def test_create_album_basic_fields(self):
        album = Album.objects.create(
            name="Test Album",
            song_count=10,
            plays_count=100,
            duration=3600.5,
            size=1024000
        )
        assert album.name == "Test Album"
        assert album.song_count == 10
        assert album.plays_count == 100
        assert album.duration == 3600.5
        assert album.size == 1024000

    def test_album_str_representation(self):
        album = Album.objects.create(name="My Album")
        assert str(album) == "My Album"

    def test_album_with_artist(self):
        artist = Artist.objects.create(name="Test Artist")
        album = Album.objects.create(name="Test Album", artist=artist)
        assert album.artist == artist
        assert album.artist.name == "Test Artist"

    def test_album_with_genre(self):
        genre = Genre.objects.create(name="Rock")
        album = Album.objects.create(name="Test Album", genre=genre)
        assert album.genre == genre
        assert album.genre.name == "Rock"

    def test_album_auto_updated_at(self):
        import time
        album = Album.objects.create(name="Test Album")
        original_updated_at = album.updated_at
        time.sleep(0.1)
        album.name = "Updated Album"
        album.save()
        assert album.updated_at >= original_updated_at


@pytest.mark.django_db
class TestTrackModel:
    def test_create_track_basic_fields(self):
        track = Track.objects.create(
            name="Test Song",
            path="/music/test.mp3",
            duration=180.5,
            size=5000000,
            suffix="mp3",
            bit_rate=320
        )
        assert track.name == "Test Song"
        assert track.path == "/music/test.mp3"
        assert track.duration == 180.5
        assert track.size == 5000000
        assert track.suffix == "mp3"
        assert track.bit_rate == 320

    def test_track_str_representation(self):
        track = Track.objects.create(name="My Song")
        assert str(track) == "My Song"

    def test_track_with_album(self):
        album = Album.objects.create(name="Test Album")
        track = Track.objects.create(name="Test Song", album=album)
        assert track.album == album

    def test_track_with_artist(self):
        artist = Artist.objects.create(name="Test Artist")
        track = Track.objects.create(name="Test Song", artist=artist)
        assert track.artist == artist

    def test_track_with_genre(self):
        genre = Genre.objects.create(name="Pop")
        track = Track.objects.create(name="Test Song", genre=genre)
        assert track.genre == genre

    def test_track_auto_created_at(self):
        track = Track.objects.create(name="Test Song")
        assert track.created_at is not None


@pytest.mark.django_db
class TestArtistModel:
    def test_create_artist_basic_fields(self):
        artist = Artist.objects.create(
            name="Test Artist",
            album_count=5,
            song_count=50,
            size=10000000
        )
        assert artist.name == "Test Artist"
        assert artist.album_count == 5
        assert artist.song_count == 50
        assert artist.size == 10000000

    def test_artist_str_representation(self):
        artist = Artist.objects.create(name="My Artist")
        assert str(artist) == "My Artist"


@pytest.mark.django_db
class TestGenreModel:
    def test_create_genre(self):
        genre = Genre.objects.create(name="Rock")
        assert genre.name == "Rock"

    def test_genre_unique_name(self):
        Genre.objects.create(name="Rock")
        with pytest.raises(Exception):
            Genre.objects.create(name="Rock")


@pytest.mark.django_db
class TestAttachmentModel:
    def _create_test_image(self, width=100, height=100):
        image = Image.new('RGB', (width, height), color='red')
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return SimpleUploadedFile(
            "test.jpg",
            buffer.read(),
            content_type="image/jpeg"
        )

    def test_create_attachment(self):
        image_file = self._create_test_image()
        attachment = Attachment.objects.create(file=image_file)
        assert attachment.file.name is not None

    def test_attachment_auto_size(self):
        image_file = self._create_test_image()
        attachment = Attachment.objects.create(file=image_file)
        assert attachment.size is not None
        assert attachment.size > 0


@pytest.mark.django_db
class TestPlaylistModel:
    def test_create_playlist(self, test_user):
        playlist = Playlist.objects.create(
            name="My Playlist",
            user=test_user,
            privacy_level="me"
        )
        assert playlist.name == "My Playlist"
        assert playlist.user == test_user
        assert playlist.privacy_level == "me"

    def test_playlist_str_representation(self, test_user):
        playlist = Playlist.objects.create(name="My Playlist", user=test_user)
        assert str(playlist) == "My Playlist"


@pytest.mark.django_db
class TestTrackFavoriteModel:
    def test_create_favorite(self, test_user):
        track = Track.objects.create(name="Test Song")
        favorite = TrackFavorite.add(track=track, user=test_user)
        assert favorite.track == track
        assert favorite.user == test_user

    def test_favorite_unique(self, test_user):
        track = Track.objects.create(name="Test Song")
        TrackFavorite.add(track=track, user=test_user)
        favorite2, created = TrackFavorite.objects.get_or_create(
            user=test_user, track=track
        )
        assert created is False

    def test_favorite_ordering(self, test_user):
        track1 = Track.objects.create(name="Song 1")
        track2 = Track.objects.create(name="Song 2")
        import time
        TrackFavorite.add(track=track1, user=test_user)
        time.sleep(0.01)
        TrackFavorite.add(track=track2, user=test_user)
        favorites = list(TrackFavorite.objects.all())
        assert favorites[0].track == track2
        assert favorites[1].track == track1


@pytest.mark.django_db
class TestFolderModel:
    def test_create_folder(self):
        folder = Folder.objects.create(
            name="Music Folder",
            path="/music/test",
            file_type="folder"
        )
        assert folder.name == "Music Folder"
        assert folder.path == "/music/test"
        assert folder.file_type == "folder"

    def test_folder_auto_uid(self):
        folder = Folder.objects.create(name="Test", path="/test")
        assert folder.uid is not None


class TestImageDimensionsValidator:
    def test_min_width_validation(self):
        validator = ImageDimensionsValidator(min_width=100)
        image_file = self._create_test_image(50, 100)
        with pytest.raises(ValidationError):
            validator(image_file)

    def test_min_height_validation(self):
        validator = ImageDimensionsValidator(min_height=100)
        image_file = self._create_test_image(100, 50)
        with pytest.raises(ValidationError):
            validator(image_file)

    def test_max_width_validation(self):
        validator = ImageDimensionsValidator(max_width=50)
        image_file = self._create_test_image(100, 100)
        with pytest.raises(ValidationError):
            validator(image_file)

    def test_max_height_validation(self):
        validator = ImageDimensionsValidator(max_height=50)
        image_file = self._create_test_image(100, 100)
        with pytest.raises(ValidationError):
            validator(image_file)

    def test_valid_image_passes(self):
        validator = ImageDimensionsValidator(min_width=50, min_height=50)
        image_file = self._create_test_image(100, 100)
        validator(image_file)

    def _create_test_image(self, width, height):
        image = Image.new('RGB', (width, height), color='red')
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return SimpleUploadedFile(
            "test.jpg",
            buffer.read(),
            content_type="image/jpeg"
        )


class TestFileValidator:
    def test_allowed_extensions_valid(self):
        validator = FileValidator(allowed_extensions=['jpg', 'png'])
        file = SimpleUploadedFile("test.jpg", b"content")
        validator(file)

    def test_allowed_extensions_invalid(self):
        validator = FileValidator(allowed_extensions=['jpg', 'png'])
        file = SimpleUploadedFile("test.exe", b"content")
        with pytest.raises(ValidationError):
            validator(file)

    def test_max_size_validation(self):
        validator = FileValidator(max_size=100)
        file = SimpleUploadedFile("test.jpg", b"x" * 200)
        with pytest.raises(ValidationError):
            validator(file)

    def test_min_size_validation(self):
        validator = FileValidator(min_size=100)
        file = SimpleUploadedFile("test.jpg", b"x" * 50)
        with pytest.raises(ValidationError):
            validator(file)


class TestDomainValidator:
    def test_valid_domain(self):
        validator = DomainValidator()
        result = validator("example.com")
        assert result == "example.com"

    def test_invalid_domain(self):
        validator = DomainValidator()
        with pytest.raises(ValidationError):
            validator("invalid domain with spaces")


class TestChunkedPath:
    def test_sanitize_filename(self):
        cp = ChunkedPath("test")
        result = cp.sanitize_filename("test/file.jpg")
        assert result == "test-file.jpg"

    def test_preserve_filename(self):
        cp = ChunkedPath("test", preserve_file_name=True)
        result = cp(None, "test.jpg")
        assert "test" in result
        assert "test.jpg" in result

    def test_not_preserve_filename(self):
        cp = ChunkedPath("test", preserve_file_name=False)
        result = cp(None, "test.jpg")
        assert "test" in result
        assert result.endswith(".jpg")
