# API 文档

## 概述

Music Tag Web 提供了两套 API：
1. **RESTful API**：基于 Django REST Framework 的标准 REST API
2. **Subsonic API**：兼容 Subsonic 协议的 API，用于第三方音乐播放器

## 认证方式

### JWT Token 认证

**获取 Token：**
```
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}
```

**响应：**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**使用 Token：**
```
Authorization: JWT <token>
```

### Session 认证

使用 Django 原生 Session 认证，需要先登录。

### Subsonic 认证

Subsonic API 使用 token-based 认证或密码认证：
- Token 认证：`?u=username&t=token&s=salt&v=1.16.0&c=client`
- 密码认证：`?u=username&p=password&v=1.16.0&c=client`

---

## RESTful API

### 基础信息

- **Base URL**: `/api/`
- **Content-Type**: `application/json`
- **响应格式**: JSON

### 通用响应格式

**成功响应：**
```json
{
  "code": 0,
  "msg": "success",
  "data": {}
}
```

**失败响应：**
```json
{
  "code": 1,
  "msg": "error message",
  "data": null
}
```

---

## 任务管理 API

### 1. 获取文件列表

**端点**: `POST /api/file_list/`

**请求参数：**
```json
{
  "file_path": "/path/to/folder",
  "sorted_fields": ["name", "update_time", "size"]
}
```

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "name": "folder_name",
      "title": "folder_name",
      "expanded": true,
      "id": 0,
      "children": [
        {
          "id": 1,
          "name": "song.mp3",
          "title": "song.mp3",
          "icon": "icon-script-file",
          "state": "null",
          "size": 5242880,
          "update_time": "2024-01-01 12:00:00"
        },
        {
          "id": 2,
          "name": "subfolder",
          "title": "subfolder",
          "icon": "icon-folder",
          "state": "null",
          "children": [],
          "size": 0,
          "update_time": "2024-01-01 12:00:00"
        }
      ],
      "icon": "icon-folder"
    }
  ]
}
```

**支持的排序字段：**
- `name`: 按文件名排序
- `update_time`: 按更新时间排序
- `size`: 按文件大小排序

---

### 2. 获取音乐 ID3 信息

**端点**: `POST /api/music_id3/`

**请求参数：**
```json
{
  "file_path": "/path/to/folder",
  "file_name": "song.mp3"
}
```

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "year": 2024,
    "comment": "",
    "lyrics": "歌词内容...",
    "duration": 245.5,
    "size": 5.0,
    "bit_rate": 320,
    "tracknumber": 1,
    "discnumber": 1,
    "artwork": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "artwork_w": 1280,
    "artwork_h": 1280,
    "artwork_size": 0.5,
    "title": "歌曲标题",
    "artist": "艺术家",
    "album": "专辑名称",
    "album_type": "album",
    "genre": "POP",
    "filename": "song.mp3",
    "albumartist": "专辑艺术家",
    "language": "zh-CN"
  }
}
```

---

### 3. 更新音乐 ID3 信息

**端点**: `POST /api/update_id3/`

**请求参数：**
```json
{
  "music_id3_info": [
    {
      "file_full_path": "/path/to/song.mp3",
      "title": "新标题",
      "artist": "新艺术家",
      "album": "新专辑",
      "year": 2024,
      "genre": "POP",
      "tracknumber": 1,
      "discnumber": 1,
      "lyrics": "新歌词...",
      "comment": "备注"
    }
  ]
}
```

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": null
}
```

---

### 4. 批量更新 ID3 信息

**端点**: `POST /api/batch_update_id3/`

**请求参数：**
```json
{
  "file_full_path": "/path/to/folder",
  "select_data": [
    {
      "name": "song1.mp3",
      "icon": "icon-script-file"
    },
    {
      "name": "song2.mp3",
      "icon": "icon-script-file"
    }
  ],
  "music_info": {
    "artist": "统一艺术家",
    "album": "统一专辑",
    "year": 2024,
    "genre": "POP"
  }
}
```

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": null
}
```

---

### 5. 批量自动刮削

**端点**: `POST /api/batch_auto_update_id3/`

**请求参数：**
```json
{
  "file_full_path": "/path/to/folder",
  "select_data": [
    {
      "name": "song.mp3",
      "icon": "icon-script-file"
    }
  ],
  "music_info": {
    "select_mode": "smart",
    "source_list": ["netease", "qmusic", "migu", "kugou"]
  }
}
```

**参数说明：**
- `select_mode`: 选择模式
  - `smart`: 智能匹配
  - `title`: 标题匹配
- `source_list`: 数据源列表
  - `netease`: 网易云音乐
  - `qmusic`: QQ 音乐
  - `migu`: 咪咕音乐
  - `kugou`: 酷狗音乐
  - `kuwo`: 酷我音乐
  - `acoustid`: 声纹识别

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": null
}
```

---

### 6. 获取歌词

**端点**: `POST /api/fetch_lyric/`

**请求参数：**
```json
{
  "resource": "netease",
  "song_id": "123456"
}
```

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": "[00:00.00]歌词第一行\n[00:05.00]歌词第二行..."
}
```

---

### 7. 根据标题搜索音乐

**端点**: `POST /api/fetch_id3_by_title/`

**请求参数：**
```json
{
  "resource": "netease",
  "title": "歌曲标题",
  "full_path": "/path/to/song.mp3"
}
```

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": "123456",
      "name": "歌曲标题",
      "artist": "艺术家",
      "artist_id": "789",
      "album": "专辑名称",
      "album_id": "456",
      "album_img": "https://example.com/cover.jpg",
      "year": "2024"
    }
  ]
}
```

---

### 8. 翻译歌词

**端点**: `POST /api/translation_lyc/`

**请求参数：**
```json
{
  "lyc": "[00:00.00]原歌词第一行\n[00:05.00]原歌词第二行..."
}
```

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": "[00:00.00]原歌词第一行\n「翻译歌词第一行」\n[00:05.00]原歌词第二行\n「翻译歌词第二行」..."
}
```

---

### 9. 整理文件夹

**端点**: `POST /api/tidy_folder/`

**请求参数：**
```json
{
  "root_path": "/path/to/root",
  "first_dir": "artist",
  "second_dir": "album",
  "file_full_path": "/path/to/folder",
  "select_data": [
    {
      "name": "song.mp3",
      "icon": "icon-script-file"
    }
  ]
}
```

**参数说明：**
- `first_dir`: 第一级目录（artist, album, genre, year）
- `second_dir`: 第二级目录（可选）

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": null
}
```

---

### 10. 上传图片

**端点**: `POST /api/upload_image/`

**请求参数：**
```
Content-Type: multipart/form-data

upload_file: <binary file data>
```

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

---

### 11. 全量扫描文件夹

**端点**: `GET /api/full_scan_folder/`

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": null
}
```

---

### 12. 获取活跃任务队列

**端点**: `GET /api/active_queue/`

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": "task-id-1",
      "name": "applications.task.tasks.full_scan_folder",
      "args": [],
      "kwargs": {}
    }
  ]
}
```

---

### 13. 清除 Celery 任务

**端点**: `GET /api/clear_celery/`

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": null
}
```

---

## 用户管理 API

### 1. 用户注册

**端点**: `POST /user/`

**请求参数：**
```json
{
  "username": "newuser",
  "password": "password123",
  "email": "user@example.com"
}
```

**响应示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com"
  }
}
```

---

## Subsonic API

### 基础信息

- **Base URL**: `/rest/`
- **协议版本**: `1.16.0`
- **响应格式**: XML 或 JSON
- **认证方式**: Token 或密码

### 通用参数

- `u`: 用户名
- `p`: 密码（hex 编码）或 `enc:token`
- `t`: Token（salted password）
- `s`: Salt
- `v`: 协议版本（`1.16.0`）
- `c`: 客户端名称
- `f`: 响应格式（`json` 或 `xml`，默认 `xml`）

### 通用响应格式

```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <!-- 具体数据 -->
</subsonic-response>
```

---

### 1. 心跳检测

**端点**: `GET /rest/ping.view`

**请求示例：**
```
GET /rest/ping.view?u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0"/>
```

---

### 2. 获取许可证

**端点**: `GET /rest/getLicense.view`

**请求示例：**
```
GET /rest/getLicense.view?u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <license valid="true" email="valid@valid.license" licenseExpires="2025-01-01T00:00:00"/>
</subsonic-response>
```

---

### 3. 获取艺术家列表

**端点**: `GET /rest/getArtists.view`

**请求示例：**
```
GET /rest/getArtists.view?u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <artists>
    <index name="A">
      <artist id="1" name="Artist A" albumCount="5" coverArt="ar-1"/>
    </index>
    <index name="B">
      <artist id="2" name="Artist B" albumCount="3" coverArt="ar-2"/>
    </index>
  </artists>
</subsonic-response>
```

---

### 4. 获取艺术家详情

**端点**: `GET /rest/getArtist.view`

**请求参数：**
- `id`: 艺术家 ID

**请求示例：**
```
GET /rest/getArtist.view?id=1&u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <artist id="1" name="Artist A" albumCount="5" coverArt="ar-1">
    <album id="10" name="Album A1" artist="Artist A" artistId="1" songCount="12" duration="3600" playCount="100" created="2024-01-01T00:00:00" coverArt="al-10"/>
    <album id="11" name="Album A2" artist="Artist A" artistId="1" songCount="10" duration="3000" playCount="80" created="2024-01-02T00:00:00" coverArt="al-11"/>
  </artist>
</subsonic-response>
```

---

### 5. 获取专辑列表

**端点**: `GET /rest/getAlbumList2.view`

**请求参数：**
- `type`: 列表类型
  - `alphabeticalByArtist`: 按艺术家字母顺序
  - `alphabeticalByName`: 按专辑名称字母顺序
  - `random`: 随机
  - `newest`: 最新
  - `frequent`: 最常播放
  - `recent`: 最近播放
  - `byGenre`: 按风格
  - `byYear`: 按年份
- `size`: 返回数量（默认 50，最大 500）
- `offset`: 偏移量
- `fromYear`: 起始年份（byYear 类型）
- `toYear`: 结束年份（byYear 类型）
- `genre`: 风格名称（byGenre 类型）

**请求示例：**
```
GET /rest/getAlbumList2.view?type=alphabeticalByArtist&size=50&offset=0&u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <albumList2>
    <album id="10" name="Album A1" artist="Artist A" artistId="1" coverArt="al-10" songCount="12" duration="3600" playCount="100" created="2024-01-01T00:00:00" year="2024" genre="POP"/>
    <album id="11" name="Album A2" artist="Artist A" artistId="1" coverArt="al-11" songCount="10" duration="3000" playCount="80" created="2024-01-02T00:00:00" year="2024" genre="POP"/>
  </albumList2>
</subsonic-response>
```

---

### 6. 获取专辑详情

**端点**: `GET /rest/getAlbum.view`

**请求参数：**
- `id`: 专辑 ID

**请求示例：**
```
GET /rest/getAlbum.view?id=10&u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <album id="10" name="Album A1" artist="Artist A" artistId="1" coverArt="al-10" songCount="12" duration="3600" playCount="100" created="2024-01-01T00:00:00" year="2024" genre="POP">
    <song id="100" parent="10" title="Song 1" album="Album A1" artist="Artist A" track="1" duration="180" bitRate="320" contentType="audio/mpeg" suffix="mp3" coverArt="al-10" path="/path/to/song1.mp3" playCount="10" created="2024-01-01T00:00:00"/>
    <song id="101" parent="10" title="Song 2" album="Album A1" artist="Artist A" track="2" duration="200" bitRate="320" contentType="audio/mpeg" suffix="mp3" coverArt="al-10" path="/path/to/song2.mp3" playCount="8" created="2024-01-01T00:00:00"/>
  </album>
</subsonic-response>
```

---

### 7. 获取歌曲详情

**端点**: `GET /rest/getSong.view`

**请求参数：**
- `id`: 歌曲 ID

**请求示例：**
```
GET /rest/getSong.view?id=100&u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <song id="100" parent="10" title="Song 1" album="Album A1" artist="Artist A" track="1" duration="180" bitRate="320" contentType="audio/mpeg" suffix="mp3" coverArt="al-10" path="/path/to/song1.mp3" playCount="10" created="2024-01-01T00:00:00" year="2024" genre="POP"/>
</subsonic-response>
```

---

### 8. 流媒体播放

**端点**: `GET /rest/stream.view`

**请求参数：**
- `id`: 歌曲 ID
- `maxBitRate`: 最大比特率（可选）
- `format`: 转码格式（可选，如 `mp3`）

**请求示例：**
```
GET /rest/stream.view?id=100&maxBitRate=320&format=mp3&u=admin&p=admin&v=1.16.0&c=myapp
```

**响应：**
音频文件流

---

### 9. 获取封面图片

**端点**: `GET /rest/getCoverArt.view`

**请求参数：**
- `id`: 封面 ID（格式：`al-{album_id}`, `ar-{artist_id}`, `at-{attachment_id}`）

**请求示例：**
```
GET /rest/getCoverArt.view?id=al-10&u=admin&p=admin&v=1.16.0&c=myapp
```

**响应：**
图片文件流

---

### 10. 获取收藏列表

**端点**: `GET /rest/getStarred2.view`

**请求示例：**
```
GET /rest/getStarred2.view?u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <starred2>
    <song id="100" parent="10" title="Song 1" album="Album A1" artist="Artist A" track="1" duration="180" bitRate="320" contentType="audio/mpeg" suffix="mp3" coverArt="al-10" path="/path/to/song1.mp3" playCount="10" created="2024-01-01T00:00:00" starred="2024-01-01T00:00:00"/>
  </starred2>
</subsonic-response>
```

---

### 11. 添加收藏

**端点**: `GET /rest/star.view`

**请求参数：**
- `id`: 歌曲 ID

**请求示例：**
```
GET /rest/star.view?id=100&u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0"/>
```

---

### 12. 取消收藏

**端点**: `GET /rest/unstar.view`

**请求参数：**
- `id`: 歌曲 ID

**请求示例：**
```
GET /rest/unstar.view?id=100&u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0"/>
```

---

### 13. 获取播放列表

**端点**: `GET /rest/getPlaylists.view`

**请求示例：**
```
GET /rest/getPlaylists.view?u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <playlists>
    <playlist id="1" name="My Playlist" owner="admin" public="false" songCount="10" duration="1800" created="2024-01-01T00:00:00" changed="2024-01-02T00:00:00"/>
  </playlists>
</subsonic-response>
```

---

### 14. 获取音乐文件夹

**端点**: `GET /rest/getMusicFolders.view`

**请求示例：**
```
GET /rest/getMusicFolders.view?u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <musicFolders>
    <musicFolder id="1" name="Music"/>
  </musicFolders>
</subsonic-response>
```

---

### 15. 获取音乐目录

**端点**: `GET /rest/getMusicDirectory.view`

**请求参数：**
- `id`: 目录 ID

**请求示例：**
```
GET /rest/getMusicDirectory.view?id=10&u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <directory id="10" parent="1" name="Artist A" starred="2024-01-01T00:00:00">
    <child id="11" parent="10" title="Album A1" artist="Artist A" isDir="true" coverArt="al-11"/>
    <child id="12" parent="10" title="Album A2" artist="Artist A" isDir="true" coverArt="al-12"/>
  </directory>
</subsonic-response>
```

---

### 16. 获取风格列表

**端点**: `GET /rest/getGenres.view`

**请求示例：**
```
GET /rest/getGenres.view?u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <genres>
    <genre songCount="100" albumCount="10">POP</genre>
    <genre songCount="80" albumCount="8">ROCK</genre>
  </genres>
</subsonic-response>
```

---

### 17. 获取扫描状态

**端点**: `GET /rest/getScanStatus.view`

**请求示例：**
```
GET /rest/getScanStatus.view?u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <scanStatus scanning="false" count="5422"/>
</subsonic-response>
```

---

### 18. 开始扫描

**端点**: `GET /rest/startScan.view`

**请求示例：**
```
GET /rest/startScan.view?u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0">
  <scanStatus scanning="true" count="5411"/>
</subsonic-response>
```

---

### 19. 播放记录

**端点**: `GET /rest/scrobble.view`

**请求参数：**
- `id`: 歌曲 ID
- `albumId`: 专辑 ID（可选）
- `submission`: 是否提交（true/false）

**请求示例：**
```
GET /rest/scrobble.view?id=100&albumId=10&submission=true&u=admin&p=admin&v=1.16.0&c=myapp
```

**响应示例：**
```xml
<subsonic-response xmlns="http://subsonic.org/restapi" status="ok" version="1.16.0"/>
```

---

## 错误码

### RESTful API 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1 | 通用错误 |
| 2 | 参数错误 |
| 3 | 认证失败 |
| 4 | 权限不足 |
| 5 | 资源不存在 |

### Subsonic API 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 10 | 必需参数缺失 |
| 20 | 协议版本不匹配 |
| 40 | 用户名错误 |
| 41 | 认证失败 |
| 50 | 用户权限不足 |
| 60 | 测试版已过期 |
| 70 | 数据未找到 |

---

## 使用示例

### Python 示例

```python
import requests

# 获取 JWT Token
response = requests.post('http://localhost:8002/api/token/', json={
    'username': 'admin',
    'password': 'admin'
})
token = response.json()['token']

# 使用 Token 访问 API
headers = {'Authorization': f'JWT {token}'}
response = requests.post(
    'http://localhost:8002/api/music_id3/',
    json={
        'file_path': '/path/to/folder',
        'file_name': 'song.mp3'
    },
    headers=headers
)
print(response.json())
```

### JavaScript 示例

```javascript
// 获取 JWT Token
const response = await fetch('http://localhost:8002/api/token/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'admin',
        password: 'admin'
    })
});
const { token } = await response.json();

// 使用 Token 访问 API
const data = await fetch('http://localhost:8002/api/music_id3/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `JWT ${token}`
    },
    body: JSON.stringify({
        file_path: '/path/to/folder',
        file_name: 'song.mp3'
    })
});
const result = await data.json();
console.log(result);
```

---

## 注意事项

1. **认证 Token 有效期**：JWT Token 默认有效期为 7 天
2. **文件路径**：所有文件路径必须是绝对路径
3. **批量操作**：批量操作建议分批进行，避免超时
4. **异步任务**：扫描和刮削操作是异步的，需要轮询任务状态
5. **文件权限**：确保应用有读取和写入音乐文件的权限
6. **并发限制**：建议控制并发请求数量，避免服务器过载

---

## 更新日志

### v1.16.0
- 添加 Subsonic API 兼容
- 支持多种音乐平台刮削
- 添加智能标签匹配
- 支持歌词翻译功能

### v1.15.0
- 添加批量操作功能
- 优化文件扫描性能
- 添加文件夹整理功能
