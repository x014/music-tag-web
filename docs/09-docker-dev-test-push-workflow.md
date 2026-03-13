# Docker 开发测试推送标准流程

本文档描述 Music Tag Web 项目的 Docker 开发、测试、推送标准流程。

---

## 流程概览

```
代码修改 → 本地构建镜像 → 本地测试验证 → 推送镜像 → CI/CD 自动构建
```

---

## 一、本地开发环境准备

### 1. 前置条件

- Docker 20.10+
- Docker Compose 1.29+
- 至少 4GB 可用内存

### 2. 配置本地部署文件

修改 `local.yml` 中的路径配置：

```yaml
volumes:
  - E:/music/mp3:/app/media:z        # 本地音乐文件夹
  - E:/music/nginx.conf:/etc/nginx/nginx.conf:ro  # nginx 配置
```

### 3. 准备 Nginx 配置

在本地创建 `nginx.conf` 文件（参考 `compose/local/nginx/nginx.conf`）。

---

## 二、本地构建镜像

### 方式一：构建开发环境镜像

```bash
docker build -f compose/local/django/Dockerfile \
  -t music_tag_web:dev \
  --build-arg BUILD_ENVIRONMENT=local .
```

### 方式二：构建生产环境镜像

```bash
docker build -f compose/prod/django/Dockerfile \
  -t registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest \
  --build-arg BUILD_ENVIRONMENT=prod .
```

### 构建参数说明

| 参数 | 说明 |
|------|------|
| `-f compose/prod/django/Dockerfile` | 指定 Dockerfile 路径 |
| `-t <镜像名:标签>` | 镜像名称和标签 |
| `--build-arg BUILD_ENVIRONMENT=prod` | 构建环境类型 |

---

## 三、本地测试验证

### 1. 启动服务

```bash
docker-compose -f local.yml up -d
```

### 2. 查看服务状态

```bash
docker-compose -f local.yml ps
docker-compose -f local.yml logs -f
```

### 3. 功能测试

```bash
# 访问应用
# 浏览器打开: http://127.0.0.1:9150/admin
# 默认账号: admin / admin

# 进入容器测试
docker exec -it music-tag-web bash
python manage.py test
python manage.py check
```

### 4. 检查各服务状态

```bash
# 检查 Django
docker logs music-tag-web

# 检查 Celery Worker
docker logs music_celeryworker

# 检查 Redis
docker exec -it music_redis redis-cli ping

# 检查 MySQL
docker exec -it music_mysql mysql -u root -p123456 -e "SHOW DATABASES;"
```

### 5. 停止服务

```bash
docker-compose -f local.yml down
```

---

## 四、推送镜像到仓库

### 1. 登录镜像仓库

```bash
# 登录阿里云镜像仓库
docker login --username=<用户名> registry.cn-hangzhou.aliyuncs.com
```

### 2. 推送镜像

```bash
# 推送镜像
docker push registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest

# 推送带版本标签的镜像
docker tag registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest \
  registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:v1.0.0
docker push registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:v1.0.0
```

### 3. 推送多平台镜像

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

## 五、CI/CD 自动化流程

项目提供两个 GitHub Actions 工作流：

### 1. 镜像构建工作流 (`build-image.yml`)

**触发条件：**
- 推送到 `main` 或 `master` 分支
- 推送 tag（如 `v1.0.0`）
- 手动触发

**功能：**
- 自动编译代码
- 构建 Docker 镜像
- 推送到阿里云镜像仓库
- 支持多平台（amd64/arm64）

**镜像标签规则：**
- 推送到分支：生成 `latest` 标签
- 推送 tag：生成版本标签（如 `v1.0.0`）和 `latest`

### 2. 镜像同步工作流 (`docker-image.yml`)

**触发条件：**
- 手动触发

**功能：**
- 从 Docker Hub 拉取已有镜像
- 推送到 GHCR 和阿里云镜像仓库
- 根据 `images.txt` 文件中的列表同步

### 3. 配置 GitHub Secrets

在 GitHub 仓库 Settings → Secrets and variables → Actions 中配置：

| Secret 名称 | 说明 |
|------------|------|
| `ALIYUN_REGISTRY` | 阿里云镜像仓库地址 |
| `ALIYUN_NAME_SPACE` | 阿里云命名空间 |
| `ALIYUN_REGISTRY_USER` | 阿里云用户名 |
| `ALIYUN_REGISTRY_PASSWORD` | 阿里云密码 |
| `GHCR_TOKEN` | GitHub Personal Access Token（可选） |

---

## 六、标准操作流程

### 开发阶段

```bash
# 1. 修改代码
# ...

# 2. 本地构建测试
docker build -f compose/local/django/Dockerfile -t music_tag_web:dev --build-arg BUILD_ENVIRONMENT=local .
docker-compose -f local.yml up -d

# 3. 测试验证
docker-compose -f local.yml logs -f
# 浏览器测试功能...

# 4. 清理环境
docker-compose -f local.yml down
```

### 发布阶段

```bash
# 1. 构建生产镜像
docker build -f compose/prod/django/Dockerfile \
  -t registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest \
  --build-arg BUILD_ENVIRONMENT=prod .

# 2. 本地测试生产镜像
# 修改 local.yml 中的 image 为新构建的镜像
docker-compose -f local.yml up -d
# 测试...

# 3. 推送镜像
docker login --username=<用户名> registry.cn-hangzhou.aliyuncs.com
docker push registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest

# 4. 或者通过 Git 推送触发 CI/CD
git add .
git commit -m "release: v1.0.0"
git tag v1.0.0
git push origin main --tags
```

---

## 七、常用命令速查

```bash
# 构建镜像
docker build -f compose/prod/django/Dockerfile -t <镜像名> --build-arg BUILD_ENVIRONMENT=prod .

# 启动服务
docker-compose -f local.yml up -d

# 查看日志
docker-compose -f local.yml logs -f

# 进入容器
docker exec -it music-tag-web bash

# 停止服务
docker-compose -f local.yml down

# 推送镜像
docker push <镜像名>

# 拉取镜像
docker pull registry.cn-hangzhou.aliyuncs.com/x014/music_tag_web:latest
```

---

## 八、注意事项

1. **构建前检查**：确保 `requirements/prod.txt` 存在
2. **路径配置**：Windows 路径使用正斜杠 `/` 或双反斜杠 `\\`
3. **端口冲突**：确保本地 9150 端口未被占用
4. **资源限制**：构建镜像需要足够的内存和磁盘空间
5. **版本标签**：发布正式版本时使用语义化版本号（如 v1.0.0）

---

## 相关文档

- [Docker 镜像管理指南](./08-docker-image-management.md) - 更详细的文档
- [部署指南](./05-deployment-guide.md) - 生产环境部署
