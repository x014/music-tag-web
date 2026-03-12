# Windows 环境依赖安装问题修复

## 问题描述

在 Windows 环境下运行 `pip install -r requirements.txt` 时，gevent 编译失败：

```
Error compiling Cython file:
src\gevent\libev\corecext.pyx:60:26: undeclared name not builtin: long
```

**原因**：
- gevent 21.12.0 不兼容 Python 3.9+
- 代码中使用了 Python 2 的 `long` 类型，Python 3.x 已移除

---

## 解决方案

### 方案一：升级 gevent 版本（推荐）

修改 `requirements/base.txt`：

```diff
- gevent==21.12.0
+ gevent==22.10.2
```

然后重新安装：

```bash
# 激活虚拟环境
venv\Scripts\activate

# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements/base.txt
```

**推荐版本**：
- Python 3.9+: `gevent==22.10.2` 或 `gevent==23.9.1`
- Python 3.10+: `gevent==23.9.1`
- Python 3.11+: `gevent==24.2.1`

### 方案二：使用预编译 wheel 包

```bash
# 激活虚拟环境
venv\Scripts\activate

# 只安装预编译的 gevent
pip install --only-binary :all: gevent==22.10.2

# 然后安装其他依赖
pip install -r requirements/base.txt
```

### 方案三：安装编译依赖（不推荐）

如果你必须使用 gevent 21.12.0，需要安装编译工具：

```bash
# 安装 Microsoft Visual C++ Build Tools
# 下载地址：https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 安装完成后，重新安装
pip install -r requirements/base.txt
```

**注意**：这个方案比较复杂，不推荐。

### 方案四：使用 Docker 部署（最简单）

如果 Windows 环境配置太麻烦，直接使用 Docker：

```bash
# 拉取镜像
docker pull xhongc/music_tag_web:latest

# 运行容器
docker run -d -p 8002:8002 \
  -v /path/to/your/music:/app/media:rw \
  -v /path/to/your/config:/app/data \
  --restart=unless-stopped \
  xhongc/music_tag_web:latest
```

**优点**：
- 不需要配置 Python 环境
- 不需要编译任何依赖
- 一键启动

---

## 完整修复步骤

### 步骤 1：修改 requirements 文件

编辑 `requirements/base.txt`，将 gevent 版本改为：

```txt
gevent==22.10.2
```

### 步骤 2：清理虚拟环境（可选）

```bash
# 删除旧的虚拟环境
rmdir /s /q venv

# 重新创建虚拟环境
python -m venv venv
```

### 步骤 3：激活虚拟环境

```bash
# Windows
venv\Scripts\activate

# 检查 Python 版本
python --version
# 应该是 Python 3.9.x 或更高
```

### 步骤 4：升级 pip

```bash
python -m pip install --upgrade pip
```

### 步骤 5：安装依赖

```bash
# 安装基础依赖
pip install -r requirements/base.txt

# 如果需要本地开发，安装本地依赖
pip install -r requirements/local.txt
```

### 步骤 6：验证安装

```bash
# 检查 gevent 是否安装成功
python -c "import gevent; print(gevent.__version__)"

# 检查 Django 是否安装成功
python -c "import django; print(django.VERSION)"
```

---

## 其他可能的依赖问题

### mysqlclient 编译失败

如果遇到 mysqlclient 编译失败：

```bash
# 使用预编译版本
pip install mysqlclient==1.4.4 --only-binary mysqlclient

# 或使用 PyMySQL 替代
pip install pymysql
```

### lxml 编译失败

如果遇到 lxml 编译失败：

```bash
# 使用预编译版本
pip install lxml==4.9.1 --only-binary lxml
```

### PyExecJS 安装失败

如果遇到 PyExecJS 安装失败：

```bash
# 安装 Node.js
# 下载地址：https://nodejs.org/

# 重新安装 PyExecJS
pip install PyExecJS==1.5.1
```

---

## 推荐的完整 requirements/base.txt

```txt
Django==2.2.6
celery==4.4.7
django-celery-beat==2.2.0
django-celery-results==1.2.1
django-cors-headers==3.2.1
django-filter==2.0.0
djangorestframework==3.8.1
python-dateutil==2.8.2
requests==2.31.0
gunicorn==20.1.0
gevent==22.10.2  # 修改这里
djangorestframework-jwt==1.11.0
music-tag==0.4.3
Pillow==9.4.0
pycryptodomex==3.17
Mako==1.0.6
django-mysql==3.8.1
redis==3.2.0
mysqlclient==1.4.4
sqlalchemy==1.4.23
PyExecJS==1.5.1
tqdm==4.65.0
lxml==4.9.1
pathos==0.3.1
```

---

## 快速修复命令

如果你只想快速修复，直接运行：

```bash
# 激活虚拟环境
venv\Scripts\activate

# 升级 gevent
pip install --upgrade gevent==22.10.2

# 继续安装其他依赖
pip install -r requirements/base.txt
```

---

## 总结

**最简单的解决方案**：
1. 修改 `requirements/base.txt` 中的 gevent 版本为 `22.10.2`
2. 重新运行 `pip install -r requirements/base.txt`

**如果还是有问题**：
- 使用 Docker 部署（最简单）
- 或使用预编译包：`pip install --only-binary :all: gevent==22.10.2`
