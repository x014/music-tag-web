# 项目概览

## 项目简介

Music Tag Web 是一款功能强大的音乐标签编辑器 Web 应用，支持编辑歌曲的标题、专辑、艺术家、歌词、封面等信息。该项目基于 Django 和 Vue.js 构建，采用前后端分离架构，支持多种音频格式的元数据查看、编辑和修改。

## 项目特点

- 支持多种音频格式：FLAC, APE, WAV, AIFF, WV, TTA, MP3, M4A, OGG, MPC, OPUS, WMA, DSF, MP4 等
- 批量自动修改（刮削）音乐标签
- 音乐指纹识别，即使没有元数据也可以识别音乐
- 整理音乐文件，按艺术家、专辑分组，或自定义多级分组
- 文件排序，按照文件名、文件大小、更新时间排序
- 批量转换音乐元数据繁体转简体，或简体转繁体
- 文件名称的拆分解包，补充缺失元数据信息
- 文本替换，批量替换音乐元数据中脏数据
- 音乐格式转换，引入 ffmpeg 支持音乐格式转换
- 整轨音乐文件的切割
- 支持多种音乐标签来源（网易云音乐、QQ音乐、酷狗音乐、酷我音乐、咪咕音乐等）
- 歌词翻译功能
- 显示操作记录
- 导出专辑封面文件，支持自定义上传专辑封面
- 适配移动端 UI，支持手机端访问
- 支持使用小爱同学播放本地音乐
- 支持网盘音乐播放
- 播放记录统计，优雅展示柱形图、折线图

## 技术栈

### 后端技术栈

- **框架**: Django 2.2.6
- **API 框架**: Django REST Framework 3.8.1
- **任务队列**: Celery 4.4.7
- **数据库**: SQLite3（默认），支持 MySQL
- **缓存**: Redis
- **Web 服务器**: Gunicorn + Gevent
- **认证**: JWT (djangorestframework-jwt 1.11.0)
- **音乐标签处理**: music-tag 0.4.3
- **图像处理**: Pillow 9.4.0
- **加密**: pycryptodomex 3.17
- **模板引擎**: Mako 1.0.6
- **跨域支持**: django-cors-headers 3.2.1
- **过滤**: django-filter 2.0.0

### 前端技术栈

- **框架**: Vue.js 2.5.2
- **路由**: Vue Router 3.0.1
- **状态管理**: Vuex 2.3.1
- **UI 组件库**: iView 3.2.2, bk-magic-vue 2.3.0
- **HTTP 客户端**: Axios 0.16.2
- **图表库**: ECharts 5.1.1
- **构建工具**: Webpack 3.6.0
- **代码编辑器**: vue-codemirror 4.0.6
- **国际化**: vue-i18n 8.11.1
- **其他**: moment.js, lodash, font-awesome, screenfull 等

### 核心依赖

- **mutagen**: 音频元数据处理
- **chromaprint**: 音频指纹识别
- **PyExecJS**: JavaScript 执行环境
- **lxml**: XML/HTML 解析
- **tqdm**: 进度条显示
- **pathos**: 并行处理

## 项目结构

```
music-tag-web/
├── applications/              # Django 应用模块
│   ├── music/                # 音乐管理应用
│   │   ├── models.py         # 音乐数据模型
│   │   ├── views.py          # 视图函数
│   │   ├── utils.py          # 工具函数
│   │   └── validators.py     # 验证器
│   ├── task/                 # 任务管理应用
│   │   ├── services/         # 业务逻辑服务
│   │   │   ├── music_resource.py    # 音乐资源服务
│   │   │   ├── acoust.py            # 声纹识别
│   │   │   ├── kugou.py             # 酷狗音乐 API
│   │   │   ├── kuwo.py              # 酷我音乐 API
│   │   │   ├── qm.py                # QQ 音乐 API
│   │   │   └── smart_tag_resource.py # 智能标签服务
│   │   ├── models.py         # 任务模型
│   │   ├── views.py          # 任务视图
│   │   └── tasks.py          # Celery 任务
│   ├── subsonic/             # Subsonic API 兼容
│   │   ├── views.py          # Subsonic 视图
│   │   ├── serializers.py    # 序列化器
│   │   └── authentication.py # 认证
│   ├── user/                 # 用户管理应用
│   └── utils/                # 公共工具
├── component/                # 核心组件
│   ├── music_tag/            # 音乐标签处理核心库
│   ├── drf/                  # Django REST Framework 扩展
│   ├── mz/                   # 音乐指纹识别
│   ├── zhconv/               # 简繁转换
│   └── translators/          # 翻译服务
├── django_vue_cli/           # Django 项目配置
│   ├── settings.py           # 项目设置
│   ├── urls.py              # URL 路由
│   └── celery_app.py        # Celery 配置
├── web/                      # Vue.js 前端项目
│   ├── src/
│   │   ├── api/             # API 接口
│   │   ├── assets/          # 静态资源
│   │   ├── components/      # Vue 组件
│   │   ├── views/           # 页面视图
│   │   ├── router/          # 路由配置
│   │   └── vuex/            # Vuex 状态管理
│   ├── build/               # 构建配置
│   └── config/              # 环境配置
├── compose/                  # Docker Compose 配置
│   ├── local/               # 本地开发环境
│   └── prod/                # 生产环境
├── requirements/             # Python 依赖
├── static/                   # 静态文件
├── templates/                # Django 模板
└── docs/                     # 项目文档
```

## 部署方式

### Docker 部署

项目提供 Docker 镜像，支持快速部署：

```bash
# 拉取镜像
docker pull xhongc/music_tag_web:latest

# 运行容器
docker run -d -p 8002:8002 \
  -v /path/to/your/music:/app/media \
  -v /path/to/your/config:/app/data \
  --restart=always \
  xhongc/music_tag_web:latest
```

### Docker Compose 部署

```yaml
version: '3'

services:
  music-tag:
    image: xhongc/music_tag_web:latest
    container_name: music-tag-web
    ports:
      - "8002:8002"
    volumes:
      - /path/to/your/music:/app/media:rw
      - /path/to/your/config:/app/data
    restart: unless-stopped
```

## 访问地址

- 默认用户名: admin
- 默认密码: admin
- 访问地址: http://127.0.0.1:8002/admin

## 许可证

本项目基于 GPL V3.0 许可证发行，仅供个人私下研究学习技术使用。

## 免责声明

禁止任何形式的商业用途，包括但不仅限于售卖/打赏/获利。本项目仅以纯粹的技术目的去学习研究，如有侵犯到任何人的合法权利，请联系作者及时处理。
