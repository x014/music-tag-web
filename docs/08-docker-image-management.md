# Docker 镜像管理指南

本文档详细介绍 Music Tag Web 项目的 Docker 镜像管理流程，包括本地构建、部署、测试、镜像上传和 NAS 下载。

---

## 目录

- [本地构建镜像](#本地构建镜像)
- [本地 Docker 部署](#本地-docker-部署)
- [本地测试](#本地测试)
- [镜像上传流程](#镜像上传流程)
- [NAS 下载镜像](#nas-下载镜像)
- [常见问题](#常见问题)

---

## 本地构建镜像

### 1. 环境准备

#### 系统要求

- Docker 20.10+
- Docker Compose 1.29+
- 至少 4GB 可用内存
- 至少 20GB 磁盘空间

#### 安装 Docker

**Windows:**
```powershell
# 下载并安装 Docker Desktop
# https://www.docker.com/products/docker-desktop
```

**macOS:**
```bash
# 使用 Homebrew 安装
brew install --cask docker
```

**Linux (Ubuntu/Debian):**
```bash
# 安装 Docker
curl -fsSL https://get.docker.com | bash

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 准备构建环境

#### 确保 requirements/prod.txt 存在

检查 `requirements/prod.txt` 文件是否存在，如果不存在则创建：

```bash
# 检查文件
ls requirements/

# 如果没有 prod.txt，创建它
echo "-r base.txt" > requirements/prod.txt
```

### 3. 构建 Docker 镜像

```bash
# 进入项目目录
cd d:\code\github\music-tag-web

# 构建镜像（生产环境）
docker build -f compose/prod/django/Dockerfile -t registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest --build-arg BUILD_ENVIRONMENT=prod .

# 或者构建开发环境镜像
docker build -f compose/local/django/Dockerfile -t music_tag_web:dev --build-arg BUILD_ENVIRONMENT=local .
```

#### 构建参数说明

| 参数 | 说明 |
|------|------|
| `-f compose/prod/django/Dockerfile` | 使用生产环境 Dockerfile |
| `-t registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest` | 镜像名称和标签 |
| `--build-arg BUILD_ENVIRONMENT=prod` | 指定生产环境依赖 |

#### 构建过程

构建过程包括以下步骤：

1. **拉取基础镜像** - `python:3.9.12-slim-bullseye`
2. **安装系统依赖** - build-essential, libpq-dev 等
3. **安装 Python 依赖** - 从 requirements/prod.txt
4. **复制启动脚本** - start, start-celeryworker, start-celerybeat
5. **复制应用代码** - 整个项目代码

### 4. 推送到私有仓库

```bash
# 登录阿里云镜像仓库
docker login --username=你的阿里云账号 registry.cn-hangzhou.aliyuncs.com

# 推送镜像
docker push registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest
```

### 5. 构建多平台镜像（可选）

如果需要构建支持多架构的镜像（amd64/arm64）：

```bash
# 创建 buildx 构建器
docker buildx create --name multiarch --driver docker-container --use

# 构建并推送多平台镜像
docker buildx build --platform linux/amd64,linux/arm64 \
  -f compose/prod/django/Dockerfile \
  -t registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest \
  --build-arg BUILD_ENVIRONMENT=prod \
  --push .
```

---

## 本地 Docker 部署

### 1. 配置本地部署

#### 修改 `local.yml` 配置

`local.yml` 是本地开发的 Docker Compose 配置文件，需要根据实际情况修改：

```yaml
services:
  django:
    image: registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest
    container_name: music-tag-web
    expose:
      - "8001"
    volumes:
      # 修改为你的本地音乐文件夹路径
      - /path/to/your/music:/app/media:z
    restart: always
    environment:
      dockerrun: "yes"
    depends_on:
      - redis
      - db
    networks:
      - internal
    command: /start

  celeryworker:
    image: registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest
    container_name: music_celeryworker
    environment:
      dockerrun: "yes"
    ports: []
    volumes:
      # 修改为你的本地音乐文件夹路径
      - /path/to/your/music:/app/media:z
    networks:
      - internal
    depends_on:
      - redis
      - db
    command: /start-celeryworker

  celerybeat:
    image: registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest
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

  redis:
    image: redis:latest
    restart: always
    container_name: music_redis
    networks:
      - internal
    expose:
      - "6379"

  db:
    image: mysql:latest
    restart: always
    environment:
      MYSQL_DATABASE: music3
      MYSQL_ROOT_PASSWORD: 123456
    networks:
      - internal
    expose:
      - "3306"

  nginx:
    image: nginx:latest
    restart: always
    container_name: music_nginx
    ports:
      - "9150:80"
    networks:
      - internal
    depends_on:
      - django
    volumes:
      # 修改为你的 nginx.conf 路径
      - /path/to/nginx.conf:/etc/nginx/nginx.conf:ro
      # 修改为你的本地音乐文件夹路径
      - /path/to/your/music:/app/media:z

networks:
  internal:
```

#### Windows 路径配置示例

```yaml
volumes:
  - E:/music/mp3:/app/media:z
  - E:/music/nginx.conf:/etc/nginx/nginx.conf:ro
```

#### macOS 路径配置示例

```yaml
volumes:
  - /Users/yourname/Music:/app/media:z
  - /Users/yourname/Music/nginx.conf:/etc/nginx/nginx.conf:ro
```

### 2. 准备 Nginx 配置

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

        location / {
            proxy_pass http://django:8001;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /media/ {
            alias /app/media/;
            autoindex on;
        }

        location /static/ {
            alias /app/static/;
        }
    }
}
```

### 3. 启动服务

```bash
# 进入项目目录
cd d:\code\github\music-tag-web

# 启动所有服务
docker-compose -f local.yml up -d

# 查看服务状态
docker-compose -f local.yml ps

# 查看日志
docker-compose -f local.yml logs -f
```

### 4. 访问应用

打开浏览器访问：`http://127.0.0.1:9150/admin`

默认账号密码：
- 用户名：`admin`
- 密码：`admin`

### 5. 常用命令

```bash
# 停止所有服务
docker-compose -f local.yml stop

# 启动所有服务
docker-compose -f local.yml start

# 重启所有服务
docker-compose -f local.yml restart

# 停止并删除所有容器
docker-compose -f local.yml down

# 停止并删除所有容器和数据卷
docker-compose -f local.yml down -v

# 查看特定服务日志
docker-compose -f local.yml logs -f django
docker-compose -f local.yml logs -f celeryworker

# 进入容器
docker exec -it music-tag-web bash

# 重新构建并启动
docker-compose -f local.yml up -d --build
```

---

## 本地测试

### 1. 功能测试

#### 测试 Django 应用

```bash
# 进入 Django 容器
docker exec -it music-tag-web bash

# 运行 Django 测试
python manage.py test

# 检查 Django 配置
python manage.py check

# 查看数据库迁移状态
python manage.py showmigrations
```

#### 测试 Celery 任务

```bash
# 查看 Celery Worker 日志
docker logs -f music_celeryworker

# 查看 Celery Beat 日志
docker logs -f music_celerybeat

# 进入容器测试 Celery
docker exec -it music-tag-web bash

# 测试 Celery 连接
python -c "from django_vue_cli.celery_app import app; print(app.control.inspect().active())"
```

#### 测试 Redis 连接

```bash
# 进入 Redis 容器
docker exec -it music_redis redis-cli

# 测试连接
127.0.0.1:6379> ping
PONG

# 查看所有键
127.0.0.1:6379> keys *

# 查看 Celery 队列
127.0.0.1:6379> llen celery
```

#### 测试 MySQL 连接

```bash
# 进入 MySQL 容器
docker exec -it music_mysql mysql -u root -p123456

# 查看数据库
mysql> SHOW DATABASES;

# 使用数据库
mysql> USE music3;

# 查看表
mysql> SHOW TABLES;
```

### 2. 性能测试

#### 使用 Apache Bench

```bash
# 安装 ab (Apache Bench)
# Ubuntu/Debian
sudo apt-get install apache2-utils

# macOS (已预装)

# Windows (通过 Apache 或 Cygwin 安装)

# 测试首页性能
ab -n 1000 -c 10 http://127.0.0.1:9150/

# 测试 API 性能
ab -n 1000 -c 10 http://127.0.0.1:9150/api/
```

#### 使用 wrk

```bash
# 安装 wrk
# Ubuntu/Debian
sudo apt-get install wrk

# macOS
brew install wrk

# 测试性能
wrk -t12 -c400 -d30s http://127.0.0.1:9150/
```

### 3. 日志检查

```bash
# 查看所有服务日志
docker-compose -f local.yml logs

# 查看最近 100 行日志
docker-compose -f local.yml logs --tail=100

# 实时查看日志
docker-compose -f local.yml logs -f --tail=50

# 查看特定时间段的日志
docker-compose -f local.yml logs --since="2024-01-01T00:00:00"
docker-compose -f local.yml logs --until="2024-01-02T00:00:00"
```

### 4. 容器健康检查

```bash
# 查看容器状态
docker ps -a

# 查看容器资源使用
docker stats

# 查看特定容器资源使用
docker stats music-tag-web music_celeryworker music_redis music_mysql

# 检查容器健康状态
docker inspect --format='{{.State.Health.Status}}' music-tag-web
```

### 5. 网络测试

```bash
# 查看网络
docker network ls

# 检查网络连接
docker exec -it music-tag-web ping redis
docker exec -it music-tag-web ping db

# 查看网络详情
docker network inspect music-tag-web_internal
```

---

## 镜像上传流程

项目提供两种 GitHub Actions 工作流：

| 工作流 | 文件 | 用途 | 触发方式 |
|--------|------|------|----------|
| **镜像同步** | `docker-image.yml` | 拉取已有镜像并推送到多个仓库 | 手动触发 |
| **镜像构建** | `build-image.yml` | 编译代码构建镜像并推送 | push/手动触发 |

### 1. 镜像构建工作流 (build-image.yml)

#### 工作流说明

此工作流会自动编译代码、构建 Docker 镜像并推送到阿里云镜像仓库。

#### 触发条件

```yaml
on:
  push:
    branches:
      - main
      - master
    tags:
      - 'v*'
  workflow_dispatch:  # 手动触发
```

#### 配置 GitHub Secrets

在 GitHub 仓库 Settings → Secrets and variables → Actions 中添加：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `ALIYUN_REGISTRY` | 阿里云镜像仓库地址 | `registry.cn-hangzhou.aliyuncs.com` |
| `ALIYUN_NAME_SPACE` | 阿里云命名空间 | `x014` |
| `ALIYUN_REGISTRY_USER` | 阿里云用户名 | `your_username` |
| `ALIYUN_REGISTRY_PASSWORD` | 阿里云密码 | `your_password` |

#### 镜像标签规则

- 推送到 `main/master` 分支：生成 `latest` 标签
- 推送 tag（如 `v1.0.0`）：生成 `v1.0.0` 和 `latest` 标签

### 2. 镜像同步工作流 (docker-image.yml)

#### 工作流说明

此工作流从 Docker Hub 拉取已有镜像，然后推送到 GHCR 和阿里云镜像仓库。

#### 镜像列表配置

镜像列表在 `images.txt` 文件中定义：

```text
xhongc/music_tag_web:latest
xhongc/music_tag_web:beta
--platform=linux/amd64 sleepnap/beidou-server-all:v1.9
--platform=linux/amd64 mysql:8.4.0
```

#### 格式说明

- 普通镜像：`namespace/image:tag`
- 指定平台：`--platform=linux/amd64 namespace/image:tag`

#### 额外 Secrets 配置

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `GHCR_TOKEN` | GitHub Personal Access Token | `ghp_xxxxxxxxxxxx` |

#### 创建 GitHub Personal Access Token

1. 访问 GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 选择权限：
   - `write:packages` - 推送镜像到 GHCR
   - `read:packages` - 拉取镜像
   - `delete:packages` - 删除镜像（可选）
4. 生成并保存 Token

### 3. 手动触发工作流

1. 进入 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择对应的工作流
4. 点击 "Run workflow"
5. 选择分支（默认 main）
6. 点击绿色的 "Run workflow" 按钮

### 4. 验证镜像上传

#### 验证阿里云镜像

```bash
# 登录阿里云镜像仓库
docker login --username=your_username registry.cn-hangzhou.aliyuncs.com

# 拉取镜像
docker pull registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest

# 查看镜像详情
docker inspect registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest
```

#### 验证 GHCR 镜像

```bash
# 登录 GHCR
echo $GHCR_TOKEN | docker login ghcr.io -u username --password-stdin

# 拉取镜像
docker pull ghcr.io/username/music_tag_web:latest

# 查看镜像详情
docker inspect ghcr.io/username/music_tag_web:latest
```

---

## NAS 下载镜像

### 1. 群晖 NAS (Synology)

#### 方法一：通过 Docker 套件

1. 打开 Docker 套件
2. 点击 "注册表"
3. 搜索 `music_tag_web`
4. 双击镜像下载
5. 选择标签（latest、beta 等）

#### 方法二：通过 SSH 命令行

```bash
# SSH 连接到 NAS
ssh admin@your-nas-ip

# 登录阿里云镜像仓库
docker login --username=your_username registry.cn-hangzhou.aliyuncs.com

# 拉取镜像
docker pull registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest

# 查看镜像
docker images | grep music_tag_web
```

#### 方法三：使用 docker-compose

1. 创建项目目录
```bash
mkdir -p /volume1/docker/music-tag-web
cd /volume1/docker/music-tag-web
```

2. 创建 `docker-compose.yml`
```yaml
services:
  django:
    image: registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest
    container_name: music-tag-web
    ports:
      - "8002:8002"
    volumes:
      - /volume1/music:/app/media:rw
      - /volume1/docker/music-tag-web/data:/app/data
    restart: always
    environment:
      dockerrun: "yes"
```

3. 启动服务
```bash
docker-compose up -d
```

### 2. 威联通 NAS (QNAP)

#### 方法一：通过 Container Station

1. 打开 Container Station
2. 点击 "创建容器"
3. 搜索 `music_tag_web`
4. 选择镜像并配置
5. 创建容器

#### 方法二：通过 SSH 命令行

```bash
# SSH 连接到 NAS
ssh admin@your-nas-ip

# 拉取镜像
docker pull registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest

# 运行容器
docker run -d \
  --name music-tag-web \
  -p 8002:8002 \
  -v /share/Music:/app/media:rw \
  -v /share/Container/music-tag-web/data:/app/data \
  --restart=always \
  -e dockerrun="yes" \
  registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest
```

### 3. 其他 NAS 系统

#### TrueNAS / FreeNAS

```bash
# 进入 Shell
# 拉取镜像
docker pull registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest

# 创建容器
docker run -d \
  --name music-tag-web \
  -p 8002:8002 \
  -v /mnt/pool/music:/app/media:rw \
  --restart=always \
  registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest
```

#### OpenMediaVault

```bash
# 安装 OMV-Extras
# 在 Web 界面启用 Docker

# SSH 连接
ssh root@your-nas-ip

# 拉取镜像
docker pull registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest

# 使用 docker-compose
cd /srv/dev-disk-by-label-data/docker
mkdir music-tag-web && cd music-tag-web

# 创建 docker-compose.yml
# 启动
docker-compose up -d
```

### 4. NAS 配置优化

#### 存储卷配置

```yaml
volumes:
  # 音乐文件目录
  - /volume1/music:/app/media:rw
  
  # 数据库和配置目录
  - /volume1/docker/music-tag-web/data:/app/data
  
  # 日志目录（可选）
  - /volume1/docker/music-tag-web/logs:/app/logs
```

#### 网络配置

```yaml
networks:
  # 使用桥接网络
  - music_network

networks:
  music_network:
    driver: bridge
```

#### 资源限制

```yaml
services:
  django:
    # 限制 CPU 使用
    cpus: 2.0
    
    # 限制内存使用
    mem_limit: 2g
    mem_reservation: 1g
    
    # 限制重启次数
    restart: on-failure:5
```

### 5. NAS 定时任务

#### 自动更新镜像

```bash
# 创建更新脚本
cat > /volume1/docker/music-tag-web/update.sh << 'EOF'
#!/bin/bash
cd /volume1/docker/music-tag-web
docker-compose pull
docker-compose up -d
docker image prune -f
EOF

# 添加执行权限
chmod +x /volume1/docker/music-tag-web/update.sh

# 添加定时任务（每周日凌晨 3 点更新）
# 在群晖：控制面板 → 任务计划 → 新增 → 计划的任务 → 用户定义的脚本
# 在威联通：控制台 → 权限 → 作业计划
```

#### 自动备份

```bash
# 创建备份脚本
cat > /volume1/docker/music-tag-web/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/volume1/backup/music-tag-web"
DATE=$(date +%Y%m%d)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
docker exec music-tag-web sqlite3 /app/data/db.sqlite3 ".backup $BACKUP_DIR/db_$DATE.sqlite3"

# 压缩备份
gzip $BACKUP_DIR/db_$DATE.sqlite3

# 删除 30 天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
EOF

# 添加执行权限
chmod +x /volume1/docker/music-tag-web/backup.sh

# 添加定时任务（每天凌晨 2 点备份）
```

---

## 常见问题

### 1. 构建时找不到 prod.txt

**问题**：`ERROR: Could not open requirements file: No such file or directory: 'prod.txt'`

**解决方案**：
```bash
# 创建 prod.txt
echo "-r base.txt" > requirements/prod.txt
```

### 2. 构建时 PyPI 镜像源 403 错误

**问题**：`ERROR: HTTP error 403 while getting https://pypi.tuna.tsinghua.edu.cn/...`

**解决方案**：
```bash
# 修改 Dockerfile，移除清华镜像源
# 将：
RUN pip wheel --wheel-dir /usr/src/app/wheels -r ${BUILD_ENVIRONMENT}.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 改为：
RUN pip wheel --wheel-dir /usr/src/app/wheels -r ${BUILD_ENVIRONMENT}.txt
```

### 3. 镜像拉取失败

**问题**：`Error: image pull failed`

**解决方案**：
```bash
# 检查网络连接
ping registry.cn-hangzhou.aliyuncs.com

# 检查 Docker 登录状态
docker logout
docker login --username=your_username registry.cn-hangzhou.aliyuncs.com

# 使用代理（如果需要）
# 编辑 /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}

# 重启 Docker
sudo systemctl restart docker
```

### 4. 容器启动失败

**问题**：容器启动后立即退出

**解决方案**：
```bash
# 查看容器日志
docker logs music-tag-web

# 查看退出代码
docker inspect music-tag-web | grep -A 5 "State"

# 常见退出代码：
# 0: 正常退出
# 1: 应用错误
# 137: 被 SIGKILL 杀死（内存不足）
# 139: 段错误

# 检查资源使用
docker stats --no-stream

# 增加内存限制
docker update --memory 2g music-tag-web
```

### 5. 端口冲突

**问题**：`Error: port is already allocated`

**解决方案**：
```bash
# 查看端口占用
# Linux/macOS
lsof -i :8002
netstat -tulpn | grep 8002

# Windows
netstat -ano | findstr :8002

# 停止占用端口的容器
docker stop $(docker ps -q --filter "publish=8002")

# 修改端口映射
# 编辑 local.yml
ports:
  - "8003:8002"  # 使用其他端口
```

### 6. 权限问题

**问题**：`Permission denied`

**解决方案**：
```bash
# Linux/macOS
# 修改目录权限
chmod -R 755 /path/to/music
chown -R www-data:www-data /path/to/music

# 或在 docker run 中指定用户
docker run -d -u $(id -u):$(id -g) ...

# Windows
# 在 Docker Desktop 设置中共享驱动器
# Settings → Shared Drives → 勾选相应驱动器
```

### 7. 数据库连接失败

**问题**：`Can't connect to MySQL server`

**解决方案**：
```bash
# 检查 MySQL 容器状态
docker ps | grep mysql
docker logs music_mysql

# 等待 MySQL 完全启动
docker exec music-tag-web python -c "
import time
import MySQLdb
for i in range(30):
    try:
        conn = MySQLdb.connect(host='db', user='root', passwd='123456', db='music3')
        print('MySQL is ready!')
        break
    except:
        print(f'Waiting for MySQL... ({i+1}/30)')
        time.sleep(2)
"

# 检查网络连接
docker exec music-tag-web ping db

# 重启服务
docker-compose -f local.yml restart db
docker-compose -f local.yml restart django
```

### 8. GitHub Actions 失败

**问题**：工作流执行失败

**解决方案**：
```bash
# 检查 Secrets 配置
# 确保所有必需的 Secrets 都已正确设置

# 检查镜像名称
# 确保 images.txt 中的镜像名称正确

# 查看详细日志
# 在 Actions 页面查看每一步的输出

# 常见错误：
# - 登录失败：检查用户名和密码
# - 推送失败：检查权限和命名空间
# - 空间不足：工作流会自动清理空间
```

### 9. NAS 性能问题

**问题**：应用运行缓慢

**解决方案**：
```yaml
# 优化资源配置
services:
  django:
    # 增加 worker 数量
    command: gunicorn -w 4 -b 0.0.0.0:8002 django_vue_cli.wsgi:application
    
    # 增加内存
    mem_limit: 4g
    
    # 使用本地存储（避免网络存储）
    volumes:
      - /mnt/ssd/music:/app/media  # 使用 SSD
```

### 10. 镜像版本不一致

**问题**：镜像版本不一致

**解决方案**：
```bash
# 强制重新拉取
docker pull --no-cache registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest

# 删除本地镜像
docker rmi registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest

# 重新拉取
docker pull registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest

# 验证镜像摘要
docker inspect --format='{{.Id}}' registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest
```

---

## 附录

### A. 常用 Docker 命令速查

```bash
# 容器管理
docker ps                    # 列出运行中的容器
docker ps -a                 # 列出所有容器
docker start <container>     # 启动容器
docker stop <container>      # 停止容器
docker restart <container>   # 重启容器
docker rm <container>        # 删除容器
docker logs <container>      # 查看日志
docker exec -it <container> bash  # 进入容器

# 镜像管理
docker images                # 列出本地镜像
docker pull <image>          # 拉取镜像
docker push <image>          # 推送镜像
docker rmi <image>           # 删除镜像
docker tag <src> <dst>       # 标记镜像
docker save -o file.tar <image>  # 导出镜像
docker load -i file.tar      # 导入镜像

# 网络管理
docker network ls            # 列出网络
docker network create <name> # 创建网络
docker network rm <name>     # 删除网络

# 数据卷管理
docker volume ls             # 列出数据卷
docker volume create <name>  # 创建数据卷
docker volume rm <name>      # 删除数据卷

# 系统管理
docker info                  # 系统信息
docker version               # 版本信息
docker system df             # 磁盘使用
docker system prune          # 清理未使用资源
```

### B. Docker Compose 命令速查

```bash
docker-compose up -d         # 后台启动
docker-compose down          # 停止并删除
docker-compose ps            # 查看状态
docker-compose logs -f       # 查看日志
docker-compose exec <service> bash  # 进入容器
docker-compose pull          # 拉取镜像
docker-compose build         # 构建镜像
docker-compose restart       # 重启服务
docker-compose stop          # 停止服务
docker-compose start         # 启动服务
```

### C. 参考链接

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [阿里云容器镜像服务](https://help.aliyun.com/product/60716.html)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

---

## 总结

本文档涵盖了 Music Tag Web 项目的完整 Docker 镜像管理流程：

1. **本地构建**：从源码构建 Docker 镜像
2. **本地部署**：使用 `local.yml` 快速部署完整的开发环境
3. **本地测试**：功能测试、性能测试、日志检查等
4. **镜像上传**：通过 GitHub Actions 自动构建/同步镜像到多个仓库
5. **NAS 下载**：在各种 NAS 系统上部署和使用镜像

通过本文档，你可以：
- 在本地从源码构建 Docker 镜像
- 推送镜像到私有仓库
- 在本地快速搭建完整的开发和测试环境
- 配置 GitHub Actions 自动化镜像构建和同步
- 在 NAS 设备上部署和管理应用
- 解决常见的 Docker 相关问题

如有问题，请参考 [常见问题](#常见问题) 章节或提交 Issue。
