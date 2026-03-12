# 部署运行文档

## 部署方式概述

Music Tag Web 提供多种部署方式，满足不同场景的需求：

1. **Docker 部署**（推荐）：快速、简单、可移植
2. **Docker Compose 部署**：完整的生产环境部署
3. **本地开发部署**：适合开发调试

---

## 环境要求

### 系统要求

- **操作系统**：Linux、macOS、Windows（支持 Docker）
- **架构**：amd64、arm64
- **内存**：建议 2GB 以上
- **磁盘空间**：建议 10GB 以上（用于音乐文件和数据库）

### 软件要求

#### Docker 部署
- Docker 20.10+
- Docker Compose 1.29+

#### 本地开发部署
- Python 3.9+
- Node.js 14+
- MySQL 5.7+ 或 SQLite 3
- Redis 5.0+

---

## 方式一：Docker 快速部署（推荐）

### 1. 拉取镜像

```bash
# 从 Docker Hub 拉取最新镜像
docker pull xhongc/music_tag_web:latest

# 或者从阿里云镜像仓库拉取
docker pull registry.cn-hangzhou.aliyuncs.com/charles0519/music_tag_web:latest
```

### 2. 运行容器

#### V2 部署方式（推荐）

```bash
docker run -d \
  --name music-tag-web \
  -p 8002:8002 \
  -v /path/to/your/music:/app/media:rw \
  -v /path/to/your/config:/app/data \
  --restart=unless-stopped \
  xhongc/music_tag_web:latest
```

**参数说明**：
- `-d`: 后台运行
- `--name`: 容器名称
- `-p 8002:8002`: 端口映射（宿主机:容器）
- `-v /path/to/your/music:/app/media:rw`: 音乐文件目录映射
- `-v /path/to/your/config:/app/data`: 配置文件目录映射
- `--restart=unless-stopped`: 自动重启策略

#### V1 部署方式（旧版）

```bash
docker run -d \
  --name music-tag-web \
  -p 8001:8001 \
  -v /path/to/your/music:/app/media:rw \
  -v /path/to/your/config:/app/data \
  --restart=unless-stopped \
  xhongc/music_tag_web:latest \
  /start
```

**注意**：V1 需要指定 `/start` 命令，V2 不需要。

### 3. 访问应用

打开浏览器访问：`http://127.0.0.1:8002/admin`

默认账号密码：
- 用户名：`admin`
- 密码：`admin`

**首次登录后请立即修改密码！**

### 4. 常用 Docker 命令

```bash
# 查看容器日志
docker logs -f music-tag-web

# 进入容器
docker exec -it music-tag-web bash

# 停止容器
docker stop music-tag-web

# 启动容器
docker start music-tag-web

# 重启容器
docker restart music-tag-web

# 删除容器
docker rm music-tag-web

# 查看容器状态
docker ps -a | grep music-tag-web
```

---

## 方式二：Docker Compose 部署（生产环境）

### 1. 准备配置文件

创建 `docker-compose.yml` 文件：

```yaml
version: '3'

services:
  # Django 应用服务
  django:
    image: xhongc/music_tag_web:latest
    container_name: music-tag-web
    expose:
      - "8002"
    volumes:
      - /path/to/your/music:/app/media:rw
      - /path/to/your/config:/app/data
    restart: always
    environment:
      dockerrun: "yes"
      # 可选：配置 MySQL
      # MYSQL_HOST: db
      # MYSQL_DATABASE: music3
      # MYSQL_USER: root
      # MYSQL_PASSWORD: 123456
    depends_on:
      - redis
      - db
    networks:
      - internal
    # V2 不需要 command
    # V1 需要添加: command: /start

  # Celery Worker 服务
  celeryworker:
    image: xhongc/music_tag_web:latest
    container_name: music_celeryworker
    environment:
      dockerrun: "yes"
    ports: []
    volumes:
      - /path/to/your/music:/app/media:rw
    networks:
      - internal
    depends_on:
      - redis
      - db
    command: /start-celeryworker

  # Celery Beat 服务
  celerybeat:
    image: xhongc/music_tag_web:latest
    container_name: music_celerybeat
    environment:
      dockerrun: "yes"
    ports: []
    networks:
      - internal
    depends_on:
      - redis
      - db
    command: /start-celerybeat

  # Redis 服务
  redis:
    image: redis:latest
    restart: always
    container_name: music_redis
    networks:
      - internal
    expose:
      - "6379"
    volumes:
      - redis_data:/data

  # MySQL 服务（可选）
  db:
    image: mysql:latest
    restart: always
    container_name: music_mysql
    environment:
      MYSQL_DATABASE: music3
      MYSQL_ROOT_PASSWORD: 123456
    networks:
      - internal
    expose:
      - "3306"
    volumes:
      - mysql_data:/var/lib/mysql

  # Nginx 服务（可选）
  nginx:
    image: nginx:latest
    restart: always
    container_name: music_nginx
    ports:
      - "80:80"
      - "443:443"
    networks:
      - internal
    depends_on:
      - django
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /path/to/your/music:/app/media:rw

networks:
  internal:
    driver: bridge

volumes:
  redis_data:
  mysql_data:
```

### 2. 配置 Nginx（可选）

创建 `nginx.conf` 文件：

```nginx
user  nginx;
worker_processes  4;

error_log  logs/error.log;
pid        logs/nginx.pid;

events {
    worker_connections  20480;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    # Gzip 压缩
    gzip on;
    gzip_comp_level    5;
    gzip_min_length    256;
    gzip_types
        text/css
        text/plain
        text/javascript
        application/javascript
        application/json;

    server {
        listen       80;
        server_name  localhost;

        # 前端页面
        location / {
            proxy_pass http://django:8002;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # 媒体文件
        location /media/ {
            alias /app/media/;
            autoindex on;
        }

        # 静态文件
        location /static/ {
            alias /app/static/;
        }
    }
}
```

### 3. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f django

# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 4. 服务说明

| 服务 | 容器名 | 端口 | 说明 |
|------|---------|------|------|
| Django | music-tag-web | 8002 | Web 应用和 API |
| Celery Worker | music_celeryworker | - | 异步任务处理 |
| Celery Beat | music_celerybeat | - | 定时任务调度 |
| Redis | music_redis | 6379 | 缓存和消息队列 |
| MySQL | music_mysql | 3306 | 数据库（可选）|
| Nginx | music_nginx | 80/443 | 反向代理（可选）|

---

## 方式三：本地开发部署

### 1. 克隆项目

```bash
git clone https://github.com/xhongc/music-tag-web.git
cd music-tag-web
```

### 2. 安装 Python 依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置数据库

#### 使用 SQLite（默认）

无需额外配置，直接使用即可。

#### 使用 MySQL（可选）

```bash
# 安装 MySQL
# Ubuntu/Debian
sudo apt-get install mysql-server

# CentOS/RHEL
sudo yum install mysql-server

# macOS
brew install mysql

# 创建数据库
mysql -u root -p
CREATE DATABASE music3 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'music_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON music3.* TO 'music_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

修改 `django_vue_cli/settings.py`：

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": 'music3',
        "USER": "music_user",
        "PASSWORD": "your_password",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    },
}
```

### 4. 配置 Redis（可选）

```bash
# 安装 Redis
# Ubuntu/Debian
sudo apt-get install redis-server

# CentOS/RHEL
sudo yum install redis

# macOS
brew install redis

# 启动 Redis
redis-server
```

修改 `django_vue_cli/settings.py`：

```python
IS_USE_CELERY = True

if IS_USE_CELERY:
    BROKER_URL = "redis://127.0.0.1:6379/1"
    CELERY_TIMEZONE = 'Asia/Shanghai'
    INSTALLED_APPS += ("django_celery_beat", "django_celery_results")
```

### 5. 数据库迁移

```bash
# 执行数据库迁移
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser
```

### 6. 启动开发服务器

```bash
# 启动 Django 开发服务器
python manage.py runserver 0.0.0.0:8002
```

### 7. 启动 Celery（可选）

```bash
# 启动 Celery Worker
celery -A django_vue_cli.celery_app worker -l info -P gevent --concurrency 10

# 启动 Celery Beat（新终端）
celery -A django_vue_cli.celery_app beat -l INFO
```

### 8. 访问应用

打开浏览器访问：`http://127.0.0.1:8002/admin`

---

## 方式四：前端开发部署

### 1. 安装 Node.js 依赖

```bash
cd web
npm install
```

### 2. 开发模式

```bash
# 启动开发服务器
npm run dev

# 或
npm start
```

访问：`http://127.0.0.1:8080`

### 3. 生产构建

```bash
# 构建生产版本
npm run build

# 构建产物在 web/dist/ 目录
```

### 4. 代码检查

```bash
# ESLint 检查
npm run lint

# 自动修复
npm run eslint
```

---

## 配置说明

### 1. Django 配置

**文件位置**：`django_vue_cli/settings.py`

#### 基础配置

```python
# 调试模式（生产环境设为 False）
DEBUG = False

# 允许的主机
ALLOWED_HOSTS = ["*"]  # 或指定域名 ["example.com"]

# 时区
TIME_ZONE = "Asia/Shanghai"

# 语言
LANGUAGE_CODE = "zh-hans"
```

#### 数据库配置

```python
# SQLite（默认）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# MySQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": 'music3',
        "USER": "root",
        "PASSWORD": "123456",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    },
}
```

#### Celery 配置

```python
# 是否启用 Celery
IS_USE_CELERY = True

if IS_USE_CELERY:
    BROKER_URL = "redis://127.0.0.1:6379/1"
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_ENABLE_UTC = False
    DJANGO_CELERY_BEAT_TZ_AWARE = False

    CELERY_TASK_SERIALIZER = "pickle"
    CELERY_ACCEPT_CONTENT = ['pickle', ]
    CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
```

#### JWT 配置

```python
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),  # Token 有效期
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_AUTH_HEADER_PREFIX': 'JWT'
}
```

#### 媒体文件配置

```python
# 媒体文件 URL
MEDIA_URL = '/media/'

# 媒体文件根目录
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Subsonic 转码格式
SUBSONIC_DEFAULT_TRANSCODING_FORMAT = "mp3"
```

### 2. 环境变量配置

**文件位置**：`local_settings.py`（需手动创建）

```python
# 数据库配置
MYSQL_HOST = "127.0.0.1"
MYSQL_DATABASE = "music3"
MYSQL_USER = "root"
MYSQL_PASSWORD = "123456"

# Redis 配置
REDIS_HOST = "127.0.0.1"
REDIS_PORT = "6379"

# Docker 运行标识
dockerrun = "yes"
```

### 3. Nginx 配置

#### 反向代理配置

```nginx
server {
    listen 80;
    server_name example.com;

    # 前端页面
    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API 接口
    location /api/ {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
    }

    # Subsonic API
    location /rest/ {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
    }

    # 媒体文件
    location /media/ {
        alias /path/to/media/;
        autoindex on;
        add_header Accept-Ranges bytes;
    }

    # 静态文件
    location /static/ {
        alias /path/to/static/;
        expires 30d;
    }
}
```

#### HTTPS 配置

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    # SSL 证书
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 其他配置同上...
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 目录结构

### 生产环境目录结构

```
/path/to/deploy/
├── music/                    # 音乐文件目录
│   ├── artist1/
│   │   ├── album1/
│   │   │   ├── song1.mp3
│   │   │   └── song2.mp3
│   │   └── album2/
│   └── artist2/
├── data/                     # 配置和数据目录
│   ├── db.sqlite3            # SQLite 数据库
│   └── attachments/          # 附件文件
└── logs/                     # 日志目录
    ├── error.log
    └── access.log
```

### Docker 容器目录结构

```
/app/
├── media/                    # 音乐文件（映射到宿主机）
│   ├── music/
│   └── attachments/
├── data/                     # 配置文件（映射到宿主机）
│   └── db.sqlite3
├── static/                   # 静态文件
├── templates/                # 模板文件
├── django_vue_cli/          # Django 项目
├── applications/             # Django 应用
├── component/               # 核心组件
├── web/                     # Vue 前端项目
├── requirements/             # Python 依赖
├── compose/                 # Docker 配置
├── manage.py                # Django 管理脚本
└── start                    # 启动脚本
```

---

## 性能优化

### 1. Gunicorn 配置

**文件位置**：`compose/local/django/start`

```bash
# Worker 数量（建议 CPU 核心数 * 2 + 1）
gunicorn -w 4 \
  -b 0.0.0.0:8002 \
  django_vue_cli.wsgi:application \
  --timeout 120 \
  --worker-class=gevent \
  --worker-connections=1000 \
  --max-requests=1000 \
  --max-requests-jitter=100
```

### 2. Celery 配置

**Worker 配置**：
```bash
# 并发数（建议 CPU 核心数 * 4）
celery -A django_vue_cli.celery_app worker \
  -l info \
  -P gevent \
  --concurrency=16 \
  --max-tasks-per-child=1000
```

**Beat 配置**：
```bash
celery -A django_vue_cli.celery_app beat \
  -l INFO \
  --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### 3. Nginx 配置

```nginx
# Worker 进程数（建议 CPU 核心数）
worker_processes 4;

# 每个 Worker 的最大连接数
events {
    worker_connections  20480;
}

# 启用 Gzip 压缩
gzip on;
gzip_comp_level 5;
gzip_min_length 256;
gzip_types text/css text/javascript application/javascript;

# 启用缓存
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;
proxy_cache_valid 200 30d;
```

### 4. 数据库优化

```sql
-- MySQL 配置
[mysqld]
# InnoDB 缓冲池大小（建议物理内存的 70-80%）
innodb_buffer_pool_size = 2G

# 查询缓存
query_cache_size = 256M
query_cache_limit = 2M

# 连接数
max_connections = 500

# 日志配置
slow_query_log = /var/log/mysql/slow.log
long_query_time = 2
```

---

## 监控与日志

### 1. 应用日志

```bash
# Django 日志
tail -f logs/django.log

# Celery Worker 日志
tail -f logs/celery_worker.log

# Celery Beat 日志
tail -f logs/celery_beat.log

# Nginx 访问日志
tail -f logs/nginx/access.log

# Nginx 错误日志
tail -f logs/nginx/error.log
```

### 2. Docker 日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f django
docker-compose logs -f celeryworker

# 查看最近 100 行日志
docker-compose logs --tail=100 django
```

### 3. 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看特定容器
docker stats music-tag-web

# 查看进程
docker exec -it music-tag-web ps aux
```

---

## 备份与恢复

### 1. 数据库备份

#### SQLite 备份

```bash
# 备份
docker exec music-tag-web cp /app/data/db.sqlite3 /backup/db.sqlite3.$(date +%Y%m%d)

# 或使用 sqlite3 命令
docker exec music-tag-web sqlite3 /app/data/db.sqlite3 ".backup /backup/db.sqlite3.$(date +%Y%m%d)"
```

#### MySQL 备份

```bash
# 备份
docker exec music_mysql mysqldump -u root -p123456 music3 > backup/music3.$(date +%Y%m%d).sql

# 压缩备份
gzip backup/music3.$(date +%Y%m%d).sql
```

### 2. 文件备份

```bash
# 备份音乐文件
tar -czf backup/music.$(date +%Y%m%d).tar.gz /path/to/music

# 备份配置文件
tar -czf backup/config.$(date +%Y%m%d).tar.gz /path/to/config
```

### 3. 数据恢复

#### SQLite 恢复

```bash
# 停止服务
docker-compose stop django

# 恢复数据库
docker exec music-tag-web cp /backup/db.sqlite3.20240101 /app/data/db.sqlite3

# 启动服务
docker-compose start django
```

#### MySQL 恢复

```bash
# 停止服务
docker-compose stop db

# 恢复数据库
docker exec -i music_mysql mysql -u root -p123456 music3 < backup/music3.20240101.sql

# 启动服务
docker-compose start db
```

---

## 故障排查

### 问题 1：容器启动失败

**症状**：`docker run` 或 `docker-compose up` 失败

**可能原因**：
- 端口被占用
- 目录权限不足
- 镜像下载失败

**解决方案**：
```bash
# 检查端口占用
netstat -tulpn | grep 8002
# 或
lsof -i :8002

# 修改端口映射
docker run -d -p 8003:8002 ...

# 检查目录权限
ls -la /path/to/music
chmod 755 /path/to/music

# 重新拉取镜像
docker pull xhongc/music_tag_web:latest
```

### 问题 2：无法访问应用

**症状**：浏览器无法打开 `http://127.0.0.1:8002`

**可能原因**：
- 防火墙阻止
- 容器未启动
- 端口映射错误

**解决方案**：
```bash
# 检查容器状态
docker ps | grep music-tag-web

# 检查容器日志
docker logs music-tag-web

# 检查防火墙
# Ubuntu/Debian
sudo ufw allow 8002

# CentOS/RHEL
sudo firewall-cmd --add-port=8002/tcp --permanent
sudo firewall-cmd --reload

# 检查端口监听
netstat -tulpn | grep 8002
```

### 问题 3：数据库连接失败

**症状**：应用报错 "Can't connect to MySQL server"

**可能原因**：
- MySQL 未启动
- 连接配置错误
- 网络问题

**解决方案**：
```bash
# 检查 MySQL 容器
docker ps | grep mysql

# 检查 MySQL 日志
docker logs music_mysql

# 测试连接
docker exec music-tag-web python -c "import MySQLdb; conn = MySQLdb.connect(host='db', user='root', passwd='123456', db='music3'); print('Connected')"

# 检查网络
docker exec music-tag-web ping db
```

### 问题 4：Celery 任务不执行

**症状**：异步任务不执行，队列积压

**可能原因**：
- Celery Worker 未启动
- Redis 连接失败
- 任务配置错误

**解决方案**：
```bash
# 检查 Celery Worker
docker ps | grep celeryworker

# 检查 Celery 日志
docker logs music_celeryworker

# 检查 Redis
docker ps | grep redis
docker logs music_redis

# 测试 Redis 连接
docker exec music-tag-web python -c "import redis; r = redis.Redis(host='redis', port=6379, db=1); print(r.ping())"

# 查看活跃任务
docker exec music-tag-web celery -A django_vue_cli.celery_app inspect active
```

### 问题 5：文件权限问题

**症状**：无法读取或写入音乐文件

**可能原因**：
- 目录权限不足
- 用户/组不匹配

**解决方案**：
```bash
# 检查目录权限
ls -la /path/to/music

# 修改权限
chmod -R 755 /path/to/music

# 修改所有者
chown -R www-data:www-data /path/to/music

# 或在 Docker 中指定用户
docker run -d -u $(id -u):$(id -g) ...
```

---

## 安全建议

### 1. 修改默认密码

首次登录后立即修改默认密码：
```bash
# 进入容器
docker exec -it music-tag-web bash

# 修改密码
python manage.py changepassword admin
```

### 2. 配置防火墙

```bash
# 只允许特定 IP 访问
sudo ufw allow from 192.168.1.0/24 to any port 8002

# 或使用 Nginx 限制
location / {
    allow 192.168.1.0/24;
    deny all;
    # ...
}
```

### 3. 启用 HTTPS

使用 Let's Encrypt 免费证书：
```bash
# 安装 certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d example.com

# 自动续期
sudo certbot renew --dry-run
```

### 4. 定期备份

设置定时备份任务：
```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点备份数据库
0 2 * * * docker exec music_mysql mysqldump -u root -p123456 music3 > /backup/music3.$(date +\%Y\%m\%d).sql

# 每周日凌晨 3 点备份文件
0 3 * * 0 tar -czf /backup/music.$(date +\%Y\%m\%d).tar.gz /path/to/music
```

---

## 更新升级

### 1. 更新镜像

```bash
# 拉取最新镜像
docker pull xhongc/music_tag_web:latest

# 停止并删除旧容器
docker stop music-tag-web
docker rm music-tag-web

# 启动新容器
docker run -d \
  --name music-tag-web \
  -p 8002:8002 \
  -v /path/to/your/music:/app/media:rw \
  -v /path/to/your/config:/app/data \
  --restart=unless-stopped \
  xhongc/music_tag_web:latest
```

### 2. Docker Compose 更新

```bash
# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d

# 查看更新日志
docker-compose logs -f
```

### 3. 数据迁移

```bash
# 进入容器
docker exec -it music-tag-web bash

# 执行迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic
```

---

## 总结

Music Tag Web 提供了多种部署方式，推荐使用 **Docker Compose** 进行生产环境部署，具有以下优势：

1. **快速部署**：一键启动所有服务
2. **环境隔离**：容器化部署，互不影响
3. **易于扩展**：水平扩展简单
4. **便于维护**：统一管理和监控

根据实际需求选择合适的部署方式，并做好备份和监控工作。
