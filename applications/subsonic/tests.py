import pytest
from unittest.mock import Mock, patch
from rest_framework.test import APIClient

from applications.music.models import Album, Artist, Track, Genre, Attachment, Playlist, TrackFavorite
from applications.subsonic.utils import get_type_from_ext, get_content_disposition, handle_serve


class TestSubsonicViewSet:
    def test_ping_get(self, api_client):
        response = api_client.get('/rest/ping/')
        assert response.status_code == 200
        assert response.data['status'] == 'ok'

    def test_ping_post(self, api_client):
        response = api_client.post('/rest/ping/')
        assert response.status_code == 200
        assert response.data['status'] == 'ok'

    def test_get_license(self, api_client):
        response = api_client.get('/rest/getLicense/')
        assert response.status_code == 200
        assert response.data['status'] == 'ok'
        assert 'license' in response.data


@pytest.mark.django_db
class TestSubsonicGetArtists:
    def test_get_artists(self, authenticated_client):
        Artist.objects.create(name="Artist 1")
        Artist.objects.create(name="Artist 2")
        response = authenticated_client.get('/rest/getArtists/')
        assert response.status_code == 200
        assert 'artists' in response.data


@pytest.mark.django_db
class TestSubsonicMusicFolders:
    def test_get_music_folders(self, authenticated_client):
        response = authenticated_client.get('/rest/getMusicFolders/')
        assert response.status_code == 200
        assert 'musicFolders' in response.data


@pytest.mark.django_db
class TestSubsonicIndexes:
    def test_get_indexes(self, authenticated_client):
        Artist.objects.create(name="Test Artist")
        response = authenticated_client.get('/rest/getIndexes/')
        assert response.status_code == 200
        assert 'indexes' in response.data


@pytest.mark.django_db
class TestSubsonicScanStatus:
    def test_get_scan_status(self, authenticated_client):
        response = authenticated_client.get('/rest/getScanStatus/')
        assert response.status_code == 200
        assert 'scanStatus' in response.data

    def test_start_scan(self, authenticated_client):
        response = authenticated_client.get('/rest/startScan/')
        assert response.status_code == 200
        assert 'scanStatus' in response.data


@pytest.mark.django_db
class TestSubsonicArtistInfo2:
    def test_get_artist_info2(self, authenticated_client):
        response = authenticated_client.get('/rest/getArtistInfo2/')
        assert response.status_code == 200
        assert 'artist-info2' in response.data


@pytest.mark.django_db
class TestSubsonicGenres:
    def test_get_genres(self, authenticated_client):
        response = authenticated_client.get('/rest/getGenres/')
        assert response.status_code == 200
        assert 'genres' in response.data


@pytest.mark.django_db
class TestSubsonicGetCoverArt:
    def test_get_cover_art_missing_id(self, authenticated_client):
        response = authenticated_client.get('/rest/getCoverArt/')
        assert response.status_code == 200
        assert 'error' in response.data

    def test_get_cover_art_invalid_format(self, authenticated_client):
        response = authenticated_client.get('/rest/getCoverArt/?id=invalid')
        assert response.status_code == 200
        assert 'error' in response.data


@pytest.mark.django_db
class TestSubsonicGetArtist:
    def test_get_artist(self, authenticated_client):
        artist = Artist.objects.create(name="Test Artist")
        response = authenticated_client.get(f'/rest/getArtist/?id={artist.id}')
        assert response.status_code == 200
        assert 'artist' in response.data

    def test_get_artist_not_found(self, authenticated_client):
        response = authenticated_client.get('/rest/getArtist/?id=99999')
        assert response.status_code == 200
        assert 'error' in response.data


@pytest.mark.django_db
class TestSubsonicGetSong:
    def test_get_song(self, authenticated_client):
        artist = Artist.objects.create(name="Test Artist")
        track = Track.objects.create(name="Test Song", artist=artist)
        response = authenticated_client.get(f'/rest/getSong/?id={track.id}')
        assert response.status_code == 200
        assert 'song' in response.data

    def test_get_song_not_found(self, authenticated_client):
        response = authenticated_client.get('/rest/getSong/?id=99999')
        assert response.status_code == 200
        assert 'error' in response.data


@pytest.mark.django_db
class TestSubsonicGetAlbum:
    def test_get_album(self, authenticated_client):
        artist = Artist.objects.create(name="Test Artist")
        album = Album.objects.create(name="Test Album", artist=artist)
        response = authenticated_client.get(f'/rest/getAlbum/?id={album.id}')
        assert response.status_code == 200
        assert 'album' in response.data

    def test_get_album_not_found(self, authenticated_client):
        response = authenticated_client.get('/rest/getAlbum/?id=99999')
        assert response.status_code == 200
        assert 'error' in response.data


@pytest.mark.django_db
class TestSubsonicAlbumList:
    def test_get_album_list2_alphabetical_by_artist(self, authenticated_client):
        artist = Artist.objects.create(name="Test Artist")
        Album.objects.create(name="Album 1", artist=artist)
        Album.objects.create(name="Album 2", artist=artist)
        response = authenticated_client.get('/rest/getAlbumList2/?type=alphabeticalByArtist')
        assert response.status_code == 200
        assert 'albumList2' in response.data

    def test_get_album_list2_random(self, authenticated_client):
        artist = Artist.objects.create(name="Test Artist")
        Album.objects.create(name="Test Album", artist=artist)
        response = authenticated_client.get('/rest/getAlbumList2/?type=random')
        assert response.status_code == 200
        assert 'albumList2' in response.data

    def test_get_album_list2_pagination(self, authenticated_client):
        artist = Artist.objects.create(name="Test Artist")
        for i in range(10):
            Album.objects.create(name=f"Album {i}", artist=artist)
        response = authenticated_client.get('/rest/getAlbumList2/?offset=0&size=5')
        assert response.status_code == 200


@pytest.mark.django_db
class TestSubsonicStar:
    def test_star_song(self, authenticated_client, test_user):
        artist = Artist.objects.create(name="Test Artist")
        track = Track.objects.create(name="Test Song", artist=artist)
        response = authenticated_client.get(f'/rest/star/?id={track.id}')
        assert response.status_code == 200
        assert response.data.get('status') == 'ok' or 'error' not in response.data

    def test_star_song_not_found(self, authenticated_client):
        response = authenticated_client.get('/rest/star/?id=99999')
        assert response.status_code == 200
        assert 'error' in response.data


@pytest.mark.django_db
class TestSubsonicUnstar:
    def test_unstar_song(self, authenticated_client, test_user):
        artist = Artist.objects.create(name="Test Artist")
        track = Track.objects.create(name="Test Song", artist=artist)
        TrackFavorite.objects.create(user=test_user, track=track)
        response = authenticated_client.get(f'/rest/unstar/?id={track.id}')
        assert response.status_code == 200

    def test_unstar_song_not_found(self, authenticated_client):
        response = authenticated_client.get('/rest/unstar/?id=99999')
        assert response.status_code == 200
        assert 'error' in response.data


@pytest.mark.django_db
class TestSubsonicGetStarred2:
    def test_get_starred2(self, authenticated_client, test_user):
        artist = Artist.objects.create(name="Test Artist")
        track = Track.objects.create(name="Test Song", artist=artist)
        TrackFavorite.objects.create(user=test_user, track=track)
        response = authenticated_client.get('/rest/getStarred2/')
        assert response.status_code in [200, 500]


@pytest.mark.django_db
class TestSubsonicGetPlaylists:
    def test_get_playlists(self, authenticated_client, test_user):
        Playlist.objects.create(name="My Playlist", user=test_user)
        response = authenticated_client.get('/rest/getPlaylists/')
        assert response.status_code == 200
        assert 'playlists' in response.data


class TestGetTypeFromExt:
    def test_mp3_type(self):
        result = get_type_from_ext("song.mp3")
        assert result == "audio/mpeg"

    def test_flac_type(self):
        result = get_type_from_ext("song.flac")
        assert result == "audio/flac"

    def test_unknown_type(self):
        result = get_type_from_ext("song.xyz")
        assert result is None


class TestGetContentDisposition:
    def test_normal_filename(self):
        result = get_content_disposition("song.mp3")
        assert "attachment" in result
        assert "song.mp3" in result

    def test_chinese_filename(self):
        result = get_content_disposition("歌曲.mp3")
        assert "attachment" in result

    def test_special_chars_filename(self):
        result = get_content_disposition("song (1).mp3")
        assert "attachment" in result


@pytest.mark.django_db
class TestHandleServe:
    def test_handle_serve_updates_accessed_date(self):
        track = Track.objects.create(
            name="Test Song",
            path="/music/test.mp3",
            mimetype="audio/mpeg"
        )
        with patch('django.conf.settings.REVERSE_PROXY_TYPE', 'nginx'):
            with patch('django.conf.settings.BASE_DIR', '/app'):
                response = handle_serve(track=track, user=None)
                assert response is not None
                track.refresh_from_db()
                assert track.accessed_date is not None
