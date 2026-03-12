# 前后端开发环境部署指南

## 概述

开发环境需要同时运行：
- **后端**：Django + Gunicorn（端口 8002）
- **前端**：Vue.js + Webpack Dev Server（端口 8080）

---

## 环境要求

### 必需软件

- **Python**：3.9+
- **Node.js**：14+
- **npm**：6+
- **Git**：用于版本控制

### 可选软件

- **MySQL**：5.7+（可选，默认使用 SQLite）
- **Redis**：5.0+（可选，用于 Celery 任务队列）
- **Docker**：20.10+（可选，用于快速部署）

---

## 部署架构

```
┌─────────────────────────────────────────────────┐
│           开发环境架构                      │
├─────────────────────────────────────────────────┤
│  后端服务（Django）                      │
│  - 端口：8002                           │
│  - 提供 API 接口                       │
│  - 提供静态文件（生产模式）               │
│  - 提供媒体文件                         │
├─────────────────────────────────────────────────┤
│  前端服务（Vue.js）                     │
│  - 端口：8080                           │
│  - 提供 UI 界面                       │
│  - 热重载（HMR）                         │
│  - 跨域调用后端 API                     │
├─────────────────────────────────────────────────┤
│  通信流程：                              │
│  前端(8080) → 后端 API(8002)            │
│  http://localhost:8080/api/* →           │
│  http://localhost:8002/api/*             │
└─────────────────────────────────────────────────┘
```

---

## 步骤一：后端部署

### 1.1 创建虚拟环境

```bash
# 进入项目目录
cd D:\code\github\music-tag-web

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 1.2 安装 Python 依赖

```bash
# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements/local.txt

# 验证安装
python -c "import django; print(django.VERSION)"
python -c "import gevent; print(gevent.__version__)"
```

### 1.3 配置数据库

#### 使用 SQLite（默认，推荐开发）

无需额外配置，直接使用。

#### 使用 MySQL（可选）

```bash
# 安装 MySQL
# Windows: 下载安装 https://dev.mysql.com/downloads/mysql/

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

### 1.4 配置 Redis（可选）

```bash
# 安装 Redis
# Windows: 下载安装 https://github.com/microsoftarchive/redis/releases

# 启动 Redis
redis-server

# 测试连接
redis-cli ping
# 应该返回 PONG
```

修改 `django_vue_cli/settings.py`：

```python
IS_USE_CELERY = True

if IS_USE_CELERY:
    BROKER_URL = "redis://127.0.0.1:6379/1"
    CELERY_TIMEZONE = 'Asia/Shanghai'
    INSTALLED_APPS += ("django_celery_beat", "django_celery_results")
```

### 1.5 数据库迁移

```bash
# 执行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 按提示输入：
# 用户名：admin
# 邮箱：admin@example.com
# 密码：admin123
```

### 1.6 启动后端服务

```bash
# 方式一：开发服务器（推荐开发）
python manage.py runserver 0.0.0.0:8002

# 方式二：生产服务器（测试生产配置）
gunicorn -w 2 -b 0.0.0.0:8002 django_vue_cli.wsgi:application --timeout 120 --worker-class=gevent
```

### 1.7 验证后端

打开浏览器访问：
- **Admin 后台**：http://localhost:8002/admin
- **API 根路径**：http://localhost:8002/api/

---

## 步骤二：前端部署

### 2.1 进入前端目录

```bash
cd web
```

### 2.2 安装 Node.js 依赖

```bash
# 安装依赖
npm install

# 或使用淘宝镜像加速
npm install --registry=https://registry.npmmirror.com

# 验证安装
npm --version
node --version
```

### 2.3 配置开发环境

检查 `web/config/index.js`：

```javascript
module.exports = {
  dev: {
    // 后端 API 地址
    assetsSubDirectory: 'static',
    assetsPublicPath: '/',
    proxyTable: {
      '/api': {
        target: 'http://localhost:8002',  // 后端地址
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        }
      },
      '/rest': {
        target: 'http://localhost:8002',  // 后端地址
        changeOrigin: true,
        pathRewrite: {
          '^/rest': '/rest'
        }
      }
    },
    host: 'localhost',
    port: 8080,
    autoOpenBrowser: false,
    errorOverlay: true,
    ...
  }
}
```

### 2.4 启动前端服务

```bash
# 开发模式（推荐）
npm run dev

# 或
npm start
```

### 2.5 验证前端

打开浏览器访问：
- **前端页面**：http://localhost:8080

---

## 步骤三：配置跨域

后端需要配置 CORS 允许前端跨域访问。

### 3.1 检查 Django CORS 配置

`django_vue_cli/settings.py` 中应该有：

```python
INSTALLED_APPS = [
    "corsheaders",
    ...
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    ...
]

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
```

### 3.2 如果没有，添加配置

在 `django_vue_cli/settings.py` 中添加：

```python
# 添加到 INSTALLED_APPS
INSTALLED_APPS = [
    "corsheaders",
    ...
]

# 添加到 MIDDLEWARE（必须在最前面）
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    ...
]

# 添加 CORS 配置
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
```

---

## 步骤四：启动 Celery（可选）

如果需要使用异步任务（如自动刮削），需要启动 Celery。

### 4.1 启动 Celery Worker

```bash
# 新开一个终端
cd D:\code\github\music-tag-web

# 激活虚拟环境
venv\Scripts\activate

# 启动 Worker
celery -A django_vue_cli.celery_app worker -l info -P gevent --concurrency=10
```

### 4.2 启动 Celery Beat（可选）

```bash
# 新开一个终端
cd D:\code\github\music-tag-web

# 激活虚拟环境
venv\Scripts\activate

# 启动 Beat
celery -A django_vue_cli.celery_app beat -l INFO
```

---

## 完整启动流程

### Windows PowerShell 启动脚本

创建 `start-dev.bat`：

```batch
@echo off
echo ========================================
echo   Music Tag Web 开发环境启动
echo ========================================

echo.
echo [1/4] 启动后端服务...
start "Django Backend" cmd /k "cd /d D:\code\github\music-tag-web && venv\Scripts\activate && python manage.py runserver 0.0.0.0:8002"

timeout /t 3 /nobreak > nul

echo.
echo [2/4] 启动前端服务...
start "Vue Frontend" cmd /k "cd /d D:\code\github\music-tag-web\web && npm run dev"

timeout /t 3 /nobreak > nul

echo.
echo [3/4] 启动 Celery Worker（可选）...
start "Celery Worker" cmd /k "cd /d D:\code\github\music-tag-web && venv\Scripts\activate && celery -A django_vue_cli.celery_app worker -l info -P gevent --concurrency=10"

timeout /t 3 /nobreak > nul

echo.
echo [4/4] 启动 Celery Beat（可选）...
start "Celery Beat" cmd /k "cd /d D:\code\github\music-tag-web && venv\Scripts\activate && celery -A django_vue_cli.celery_app beat -l INFO"

echo.
echo ========================================
echo   所有服务已启动！
echo ========================================
echo.
echo 后端: http://localhost:8002
echo 前端: http://localhost:8080
echo Admin: http://localhost:8002/admin
echo.
pause
```

### Linux/macOS 启动脚本

创建 `start-dev.sh`：

```bash
#!/bin/bash

echo "========================================"
echo "  Music Tag Web 开发环境启动"
echo "========================================"

echo ""
echo "[1/4] 启动后端服务..."
cd /path/to/music-tag-web
source venv/bin/activate
python manage.py runserver 0.0.0.0:8002 &
BACKEND_PID=$!

sleep 3

echo ""
echo "[2/4] 启动前端服务..."
cd web
npm run dev &
FRONTEND_PID=$!

sleep 3

echo ""
echo "[3/4] 启动 Celery Worker（可选）..."
cd ..
celery -A django_vue_cli.celery_app worker -l info -P gevent --concurrency=10 &
WORKER_PID=$!

sleep 3

echo ""
echo "[4/4] 启动 Celery Beat（可选）..."
celery -A django_vue_cli.celery_app beat -l INFO &
BEAT_PID=$!

echo ""
echo "========================================"
echo "  所有服务已启动！"
echo "========================================"
echo ""
echo "后端: http://localhost:8002"
echo "前端: http://localhost:8080"
echo "Admin: http://localhost:8002/admin"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID $WORKER_PID $BEAT_PID; exit" INT TERM

wait
```

使用脚本：

```bash
# Windows
start-dev.bat

# Linux/macOS
chmod +x start-dev.sh
./start-dev.sh
```

---

## 访问地址

启动成功后，可以访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端页面** | http://localhost:8080 | Vue.js 开发服务器 |
| **后端 API** | http://localhost:8002/api/ | RESTful API |
| **Subsonic API** | http://localhost:8002/rest/ | Subsonic 兼容 API |
| **Admin 后台** | http://localhost:8002/admin | Django Admin |

**默认账号**：
- 用户名：`admin`
- 密码：`admin`

---

## 开发工作流

### 1. 修改后端代码

```bash
# 修改 Python 代码
# Django 会自动重载（开发模式）
# 无需重启服务
```

### 2. 修改前端代码

```bash
# 修改 Vue.js 代码
# Webpack Dev Server 会自动热重载
# 无需重启服务
```

### 3. 测试 API

使用 Postman 或 curl 测试：

```bash
# 获取 Token
curl -X POST http://localhost:8002/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# 调用 API
curl -X GET http://localhost:8002/api/file_list/ \
  -H "Authorization: JWT <token>"
```

### 4. 查看日志

```bash
# 后端日志（终端输出）
# 直接在运行后端的终端查看

# 前端日志（浏览器控制台）
# 按 F12 打开开发者工具
```

---

## 常见问题

### 问题 1：端口被占用

**症状**：`Address already in use`

**解决方案**：

```bash
# Windows: 查找占用端口的进程
netstat -ano | findstr :8002
netstat -ano | findstr :8080

# 结束进程
taskkill /PID <进程ID> /F

# 或修改端口
# 后端：python manage.py runserver 0.0.0.0:8003
# 前端：修改 web/config/index.js 中的 port
```

### 问题 2：跨域错误

**症状**：浏览器控制台显示 CORS 错误

**解决方案**：

检查 `django_vue_cli/settings.py`：

```python
CORS_ORIGIN_WHITELIST = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
```

### 问题 3：前端无法连接后端

**症状**：Network Error

**解决方案**：

1. 检查后端是否启动
2. 检查端口是否正确
3. 检查防火墙设置

```bash
# 测试后端连接
curl http://localhost:8002/api/
```

### 问题 4：npm install 失败

**症状**：依赖安装失败

**解决方案**：

```bash
# 清理缓存
npm cache clean --force

# 使用淘宝镜像
npm install --registry=https://registry.npmmirror.com

# 或使用 cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

---

## 开发工具推荐

### VS Code 插件

- **Python**：Python 代码支持
- **Vetur**：Vue.js 代码支持
- **ESLint**：代码检查
- **Prettier**：代码格式化
- **GitLens**：Git 增强

### 浏览器插件

- **Vue.js devtools**：Vue 调试工具
- **React Developer Tools**：如果使用 React
- **Postman**：API 测试

---

## 性能优化

### 1. 后端优化

```python
# django_vue_cli/settings.py

# 调试模式（开发时 True，生产时 False）
DEBUG = True

# 日志级别
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

### 2. 前端优化

```javascript
// web/config/index.js

// 关闭 source map（提高构建速度）
productionSourceMap: false,

// 开启 Gzip 压缩
gzip: true,

// 启用代码分割
chunks: true,
```

---

## 总结

### 开发环境启动清单

- [ ] Python 3.9+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] Python 依赖已安装
- [ ] 数据库已配置并迁移
- [ ] 后端服务已启动（端口 8002）
- [ ] Node.js 14+ 已安装
- [ ] 前端依赖已安装
- [ ] 前端服务已启动（端口 8080）
- [ ] CORS 已配置
- [ ] Celery 已启动（可选）

### 快速启动命令

```bash
# 终端 1：后端
cd D:\code\github\music-tag-web
venv\Scripts\activate
python manage.py runserver 0.0.0.0:8002

# 终端 2：前端
cd D:\code\github\music-tag-web\web
npm run dev

# 终端 3：Celery（可选）
cd D:\code\github\music-tag-web
venv\Scripts\activate
celery -A django_vue_cli.celery_app worker -l info -P gevent --concurrency=10
```

### 访问应用

- 前端：http://localhost:8080
- 后端：http://localhost:8002/api/
- Admin：http://localhost:8002/admin

祝开发顺利！
