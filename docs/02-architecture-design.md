# 架构设计文档

## 系统架构概述

Music Tag Web 采用前后端分离的架构设计，基于 Django REST Framework 和 Vue.js 构建，通过 Celery 实现异步任务处理，支持 Docker 容器化部署。

## 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Web 浏览器  │  │   移动端     │  │  Subsonic   │         │
│  │   (Vue.js)   │  │   (响应式)   │  │   客户端     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Nginx 反向代理                            │
│              (静态文件服务 / 负载均衡 / SSL)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Django API  │    │  Django API  │    │  Django API  │
│  (Gunicorn)  │    │  (Gunicorn)  │    │  (Gunicorn)  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Django 应用层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Task API    │  │  Music API   │  │  Subsonic    │       │
│  │  (任务管理)   │  │  (音乐管理)   │  │  API 兼容    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  User API    │  │  Music Tag   │  │  Translation │       │
│  │  (用户管理)   │  │  (标签处理)   │  │  (翻译服务)   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Celery      │    │  SQLite/     │    │  Redis       │
│  Worker      │    │  MySQL       │    │  (缓存/队列)  │
│  (异步任务)   │    │  (数据存储)   │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      外部服务层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  网易云音乐   │  │  QQ 音乐     │  │  酷狗音乐     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  酷我音乐     │  │  咪咕音乐     │  │  Acoustid    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## 技术架构分层

### 1. 表现层 (Presentation Layer)

**前端技术栈：**
- Vue.js 2.5.2：前端框架
- Vue Router 3.0.1：路由管理
- Vuex 2.3.1：状态管理
- iView 3.2.2 / bk-magic-vue 2.3.0：UI 组件库
- Axios 0.16.2：HTTP 客户端
- ECharts 5.1.1：数据可视化

**主要功能模块：**
- 音乐文件浏览器
- 标签编辑器
- 批量操作工具
- 播放统计图表
- 用户管理界面

### 2. 应用层 (Application Layer)

**后端技术栈：**
- Django 2.2.6：Web 框架
- Django REST Framework 3.8.1：API 框架
- djangorestframework-jwt 1.11.0：JWT 认证
- django-cors-headers 3.2.1：跨域支持
- django-filter 2.0.0：查询过滤

**核心应用模块：**

#### Task 应用 ([applications/task/](applications/task/))
- **功能**：任务管理和异步处理
- **主要组件**：
  - [views.py](applications/task/views.py)：任务 API 视图
  - [tasks.py](applications/task/tasks.py)：Celery 异步任务
  - [services/](applications/task/services/)：业务逻辑服务
    - [music_resource.py](applications/task/services/music_resource.py)：音乐资源服务
    - [acoust.py](applications/task/services/acoust.py)：声纹识别
    - [smart_tag_resource.py](applications/task/services/smart_tag_resource.py)：智能标签
  - [models.py](applications/task/models.py)：任务数据模型

#### Music 应用 ([applications/music/](applications/music/))
- **功能**：音乐数据管理
- **主要组件**：
  - [models.py](applications/music/models.py)：音乐数据模型
    - Track：歌曲模型
    - Album：专辑模型
    - Artist：艺术家模型
    - Genre：风格模型
    - Folder：文件夹模型
  - [views.py](applications/music/views.py)：音乐 API 视图
  - [utils.py](applications/music/utils.py)：工具函数

#### Subsonic 应用 ([applications/subsonic/](applications/subsonic/))
- **功能**：Subsonic API 兼容层
- **主要组件**：
  - [views.py](applications/subsonic/views.py)：Subsonic API 视图
  - [serializers.py](applications/subsonic/serializers.py)：数据序列化
  - [authentication.py](applications/subsonic/authentication.py)：认证处理

#### User 应用 ([applications/user/](applications/user/))
- **功能**：用户管理
- **主要组件**：
  - [models.py](applications/user/models.py)：用户模型
  - [views.py](applications/user/views.py)：用户 API 视图

### 3. 业务逻辑层 (Business Logic Layer)

#### 音乐标签处理 ([component/music_tag/](component/music_tag/))
- **功能**：音频元数据处理核心库
- **支持的格式**：
  - MP3 (ID3)
  - FLAC (Vorbis)
  - M4A (MP4)
  - OGG (Vorbis)
  - APE (APEv2)
  - WAV (RIFF)
  - AIFF (AIFF)
  - WMA (ASF)
  - DSF (DSD)
  - 等其他格式

- **主要模块**：
  - [file.py](component/music_tag/file.py)：文件处理基类
  - [id3.py](component/music_tag/id3.py)：ID3 标签处理
  - [flac.py](component/music_tag/flac.py)：FLAC 标签处理
  - [mp4.py](component/music_tag/mp4.py)：MP4 标签处理
  - [vorbis.py](component/music_tag/vorbis.py)：Vorbis 标签处理

#### 音乐资源服务 ([applications/task/services/music_resource.py](applications/task/services/music_resource.py))
- **功能**：从各大音乐平台获取音乐信息
- **支持的平台**：
  - 网易云音乐 (NetEaseMusicClient)
  - QQ 音乐 (QmusicClient)
  - 酷狗音乐 (KugouClient)
  - 酷我音乐 (KuwoClient)
  - 咪咕音乐 (MiGuMusicClient)
  - Acoustid (AcoustidClient)：声纹识别
  - Smart Tag (SmartTagClient)：智能标签匹配

#### 智能标签服务 ([applications/task/services/smart_tag_resource.py](applications/task/services/smart_tag_resource.py))
- **功能**：多平台智能匹配音乐标签
- **匹配算法**：
  - 标题匹配 (title_score)
  - 艺术家匹配 (artist_score)
  - 专辑匹配 (album_score)
  - 综合评分排序

### 4. 数据访问层 (Data Access Layer)

**数据库：**
- SQLite3（默认）
- MySQL（可选）

**主要数据模型：**

#### Track 模型 ([applications/music/models.py#L52](applications/music/models.py#L52))
```python
class Track(models.Model):
    name = models.CharField(default='', max_length=255)
    path = models.CharField(default='', max_length=255)
    album = models.ForeignKey('Album', ...)
    artist = models.ForeignKey('Artist', ...)
    has_cover_art = models.BooleanField(default=False)
    track_number = models.IntegerField(default=0)
    disc_number = models.IntegerField(default=0)
    plays_count = models.IntegerField("播放量", default=0)
    year = models.IntegerField(default=0, null=True)
    size = models.IntegerField("文件大小", default=0)
    suffix = models.CharField("后缀", default='', max_length=255)
    duration = models.FloatField("歌曲时长s", default=0)
    bit_rate = models.IntegerField(default=0)
    genre = models.ForeignKey('Genre', ...)
    lyrics = models.TextField(null=True)
    # MusicBrainz 字段
    mbz_track_id = models.CharField(default='', max_length=255)
    mbz_album_id = models.CharField(default='', max_length=255)
    mbz_artist_id = models.CharField(default='', max_length=255)
```

#### Album 模型 ([applications/music/models.py#L12](applications/music/models.py#L12))
```python
class Album(models.Model):
    name = models.CharField("专辑名称", max_length=255)
    artist = models.ForeignKey('Artist', ...)
    all_artist_ids = ListTextField(base_field=models.IntegerField())
    max_year = models.IntegerField(default=0)
    song_count = models.IntegerField("歌曲统计", default=-1)
    plays_count = models.IntegerField("播放次数", default=0)
    duration = models.FloatField("歌曲时长s", default=0)
    genre = models.ForeignKey('Genre', ...)
    attachment_cover = models.ForeignKey('Attachment', ...)
    # MusicBrainz 字段
    mbz_album_id = models.CharField(max_length=255)
    mbz_album_artist_id = models.CharField(max_length=255)
```

#### Artist 模型 ([applications/music/models.py#L93](applications/music/models.py#L93))
```python
class Artist(models.Model):
    name = models.CharField(max_length=255)
    album_count = models.IntegerField(default=0)
    song_count = models.IntegerField(default=0)
    size = models.IntegerField(default=0)
    mbz_artist_id = models.CharField(max_length=255)
    attachment_cover = models.ForeignKey('Attachment', ...)
    similar_artists = models.CharField(max_length=255)
    external_url = models.CharField(max_length=255)
```

#### Folder 模型 ([applications/music/models.py#L199](applications/music/models.py#L199))
```python
class Folder(models.Model):
    name = models.CharField(max_length=256)
    path = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_scan_time = models.DateTimeField(auto_now=True)
    file_type = models.CharField(max_length=32, default='folder')
    uid = models.UUIDField(default=uuid.uuid4)
    parent_id = models.UUIDField(null=True)
    state = models.CharField(max_length=32, default='none')
```

### 5. 基础设施层 (Infrastructure Layer)

#### 任务队列 ([django_vue_cli/celery_app.py](django_vue_cli/celery_app.py))
- **Celery 4.4.7**：分布式任务队列
- **Redis**：消息代理和结果存储
- **主要任务**：
  - [full_scan_folder](applications/task/tasks.py#L28)：全量扫描文件夹
  - [update_scan_folder](applications/task/tasks.py#L105)：增量扫描文件夹
  - [scan_music_id3](applications/task/tasks.py#L222)：扫描音乐 ID3 信息
  - [batch_auto_tag_task](applications/task/tasks.py#L246)：批量自动刮削
  - [tidy_folder_task](applications/task/tasks.py#L305)：整理文件夹

#### 缓存层
- **Redis**：
  - 任务队列存储
  - 会话存储
  - 缓存热点数据

#### 文件存储
- **本地文件系统**：
  - `/app/media`：音乐文件存储
  - `/app/data`：配置和数据文件

## 数据流设计

### 1. 音乐扫描流程

```
用户触发扫描
    ↓
Celery 任务创建
    ↓
遍历文件系统
    ↓
识别音频文件
    ↓
提取 ID3 信息
    ↓
存储到数据库
    ↓
返回扫描结果
```

### 2. 标签编辑流程

```
用户选择文件
    ↓
读取 ID3 信息
    ↓
显示标签信息
    ↓
用户编辑标签
    ↓
验证输入
    ↓
写入文件
    ↓
更新数据库
    ↓
返回成功结果
```

### 3. 自动刮削流程

```
用户选择文件
    ↓
创建刮削任务
    ↓
Celery 异步处理
    ↓
从文件名提取信息
    ↓
多平台搜索匹配
    ↓
智能评分排序
    ↓
选择最佳匹配
    ↓
写入标签
    ↓
更新任务状态
```

### 4. Subsonic API 流程

```
Subsonic 客户端请求
    ↓
Nginx 反向代理
    ↓
Subsonic 视图处理
    ↓
认证验证
    ↓
查询数据库
    ↓
序列化数据
    ↓
返回 XML/JSON 响应
```

## API 设计

### RESTful API

**基础路径**：`/api/`

**主要端点**：

#### 任务管理 API
- `POST /api/file_list/`：获取文件列表
- `POST /api/music_id3/`：获取音乐 ID3 信息
- `POST /api/update_id3/`：更新音乐 ID3 信息
- `POST /api/batch_update_id3/`：批量更新 ID3 信息
- `POST /api/batch_auto_update_id3/`：批量自动刮削
- `POST /api/fetch_lyric/`：获取歌词
- `POST /api/fetch_id3_by_title/`：根据标题搜索音乐
- `POST /api/translation_lyc/`：翻译歌词
- `POST /api/tidy_folder/`：整理文件夹
- `POST /api/upload_image/`：上传图片
- `GET /api/full_scan_folder/`：全量扫描文件夹
- `GET /api/active_queue/`：获取活跃任务队列

#### 用户管理 API
- `POST /user/`：用户注册
- `POST /api/token/`：获取 JWT Token

### Subsonic API

**基础路径**：`/rest/`

**主要端点**：
- `GET /rest/ping.view`：心跳检测
- `GET /rest/getLicense.view`：获取许可证
- `GET /rest/getArtists.view`：获取艺术家列表
- `GET /rest/getArtist.view`：获取艺术家详情
- `GET /rest/getAlbum.view`：获取专辑详情
- `GET /rest/getSong.view`：获取歌曲详情
- `GET /rest/stream.view`：流媒体播放
- `GET /rest/getAlbumList2.view`：获取专辑列表
- `GET /rest/getStarred2.view`：获取收藏列表
- `GET /rest/star.view`：添加收藏
- `GET /rest/unstar.view`：取消收藏

## 安全设计

### 认证机制
- **JWT Token**：基于 djangorestframework-jwt
- **Session 认证**：Django 原生 Session
- **Basic 认证**：Subsonic API 兼容

### 权限控制
- **Django REST Framework 权限类**：
  - `IsAuthenticated`：需要认证
  - `IsAdminUser`：管理员权限

### 数据安全
- **密码加密**：Django 原生密码哈希
- **SQL 注入防护**：ORM 参数化查询
- **XSS 防护**：Django 模板自动转义
- **CSRF 防护**：Django CSRF 中间件

## 性能优化

### 数据库优化
- **批量操作**：使用 `bulk_create`、`bulk_update`
- **索引优化**：为常用查询字段添加索引
- **查询优化**：使用 `select_related`、`prefetch_related`

### 缓存策略
- **Redis 缓存**：热点数据缓存
- **静态文件缓存**：Nginx 静态文件服务
- **CDN 加速**：静态资源 CDN 分发

### 异步处理
- **Celery 任务队列**：耗时任务异步处理
- **并发处理**：ThreadPoolExecutor 并发请求

## 部署架构

### Docker 容器化

**容器组成**：
- **Django 容器**：Web 应用和 API 服务
- **Celery Worker 容器**：异步任务处理
- **Celery Beat 容器**：定时任务调度
- **Nginx 容器**：反向代理和静态文件服务
- **Redis 容器**：缓存和消息队列
- **MySQL 容器**（可选）：数据存储

### 网络架构

```
Internet
    ↓
Nginx (80/443)
    ↓
Django (8002)
    ↓
Celery Worker
    ↓
Redis (6379)
    ↓
MySQL (3306)
```

### 环境配置

**本地开发环境** ([compose/local/](compose/local/))
- 开发工具配置
- 调试模式开启
- 热重载支持

**生产环境** ([compose/prod/](compose/prod/))
- 生产优化配置
- 日志收集
- 监控告警

## 扩展性设计

### 水平扩展
- **无状态设计**：Django 应用无状态
- **负载均衡**：Nginx 负载均衡
- **分布式任务**：Celery 分布式任务队列

### 垂直扩展
- **数据库优化**：读写分离、分库分表
- **缓存优化**：Redis 集群
- **文件存储**：对象存储（S3、OSS）

### 插件化设计
- **音乐平台扩展**：通过 `MusicResource` 接口扩展
- **标签格式扩展**：通过 `music_tag` 库扩展
- **翻译服务扩展**：通过 `translators` 模块扩展

## 监控与日志

### 日志系统
- **Django 日志**：应用日志
- **Celery 日志**：任务日志
- **Nginx 日志**：访问日志和错误日志

### 监控指标
- **系统指标**：CPU、内存、磁盘、网络
- **应用指标**：请求响应时间、错误率、任务队列长度
- **业务指标**：用户活跃度、音乐文件数量、播放统计

## 总结

Music Tag Web 采用现代化的前后端分离架构，具有良好的可扩展性和可维护性。通过 Docker 容器化部署，可以快速搭建和扩展系统。异步任务处理机制确保了系统的响应性能，多平台音乐资源集成提供了丰富的数据来源。
