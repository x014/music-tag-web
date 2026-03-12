# 自动刮削功能文档

## 功能概述

自动刮削功能是 Music Tag Web 的核心功能之一，它能够从多个音乐平台（网易云音乐、QQ音乐、酷狗音乐、酷我音乐、咪咕音乐等）自动获取音乐信息，并智能匹配后写入到本地音乐文件的 ID3 标签中。

### 主要特性

- **多数据源支持**：支持 6+ 个主流音乐平台
- **智能匹配算法**：基于繁简转换、包含匹配的评分系统
- **批量处理**：支持批量刮削多个文件或整个文件夹
- **异步任务**：基于 Celery 的异步处理，不阻塞用户操作
- **容错机制**：单个文件失败不影响其他文件处理
- **实时状态跟踪**：实时更新刮削任务状态（成功/失败）
- **两种匹配模式**：智能模式和简单模式，适应不同场景

---

## 架构设计

### 整体架构

```
用户选择文件
    ↓
┌─────────────────────────────────────┐
│  API 层 (RESTful)                │
│  batch_auto_update_id3             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  任务队列层 (Celery)              │
│  batch_auto_tag_task              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  匹配逻辑层                      │
│  match_song                      │
│  - match_score                   │
│  - match_artist                  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  数据源层 (MusicResource)         │
│  - NetEaseMusicClient            │
│  - QmusicClient                 │
│  - MiGuMusicClient              │
│  - KugouClient                 │
│  - KuwoClient                  │
│  - AcoustidClient              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  标签写入层 (save_music)         │
│  - 写入 ID3 标签                │
│  - 写入歌词                     │
│  - 写入封面                     │
└─────────────────────────────────────┘
```

### 代码文件结构

```
applications/task/
├── views.py                    # API 入口层
│   └── batch_auto_update_id3   # 批量刮削 API
├── tasks.py                    # 异步任务层
│   └── batch_auto_tag_task     # 刮削任务
├── utils.py                    # 匹配逻辑层
│   ├── match_song              # 歌曲匹配主函数
│   ├── match_score            # 字符串匹配评分
│   └── match_artist          # 艺术家匹配
└── services/
    ├── music_resource.py       # 数据源层
    │   ├── MusicResource     # 数据源工厂类
    │   ├── NetEaseMusicClient
    │   ├── QmusicClient
    │   ├── MiGuMusicClient
    │   ├── KugouClient
    │   ├── KuwoClient
    │   └── AcoustidClient
    └── update_ids.py          # 标签写入层
        └── save_music        # 保存音乐标签
```

---

## 核心流程

### 完整刮削流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 用户触发刮削                                        │
│    - 选择文件/文件夹                                      │
│    - 选择数据源（netease, qmusic, migu, kugou...）       │
│    - 选择匹配模式（smart/simple）                          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. API 接收请求                                         │
│    - 验证请求数据                                        │
│    - 生成批次时间戳                                        │
│    - 创建 TaskRecord 记录                                  │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 启动异步任务                                         │
│    - batch_auto_tag_task(timestamp, source_list, mode)      │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 处理文件夹（如果有）                                   │
│    - 扫描文件夹内的音频文件                                  │
│    - 为每个文件创建 TaskRecord                              │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 逐个文件刮削                                         │
│    for task in task_list:                                 │
│        for resource in source_list:                          │
│            match_song(resource, task.path, mode)             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. 读取本地文件信息                                       │
│    - 提取文件名                                           │
│    - 读取现有 ID3 标签（title, artist, album）             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. 从数据源搜索                                          │
│    - 使用标题搜索                                          │
│    - 获取候选歌曲列表                                        │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. 智能匹配评分                                          │
│    for song in search_results:                            │
│        - 计算标题匹配分                                       │
│        - 计算艺术家匹配分                                     │
│        - 计算专辑匹配分                                       │
│        - 累加总分                                           │
│        - 判断是否匹配成功                                       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 9. 匹配成功？                                           │
│    ├─ 是 → 获取歌词 → 写入标签 → 标记成功 → 尝试下一个文件          │
│    └─ 否 → 尝试下一个数据源 → 全部失败 → 标记失败 → 尝试下一个文件       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 10. 更新任务状态                                         │
│     - 更新 TaskRecord 状态（success/failed）                │
│     - 创建/更新 Task 记录（用于前端显示）                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 代码实现详解

### 1. API 入口层

**文件位置**：[applications/task/views.py#L188](applications/task/views.py#L188)

**函数**：`batch_auto_update_id3`

**功能**：接收用户请求，创建任务记录，启动异步刮削任务

```python
@action(methods=['POST'], detail=False)
def batch_auto_update_id3(self, request, *args, **kwargs):
    """
    批量自动刮削 API
    
    请求参数：
        file_full_path: 文件所在目录路径
        select_data: 选择的文件/文件夹列表
        music_info: 刮削配置
            - select_mode: 匹配模式（smart/simple）
            - source_list: 数据源列表
    
    响应：
        code: 0 成功
        msg: 提示信息
        data: null
    """
    # 1. 获取并验证请求数据
    validate_data = self.is_validated_data(request.data)
    full_path = validate_data['file_full_path']      # 文件所在目录
    select_data = validate_data['select_data']        # 选择的文件/文件夹
    music_info = validate_data['music_info']
    
    # 2. 获取刮削配置
    select_mode = music_info["select_mode"]          # 匹配模式
    source_list = music_info.get("source_list", [])  # 数据源列表
    
    # 3. 生成批次时间戳（用于标识这次刮削任务）
    timestamp = str(int(time.time() * 1000))
    
    # 4. 批量创建任务记录
    bulk_set = []
    for each in select_data:
        name = each.get("name")
        song_name = ".".join(name.split(".")[:-1])  # 去掉文件扩展名
        bulk_set.append(TaskRecord(**{
            "song_name": song_name,
            "full_path": f"{full_path}/{name}",
            "icon": each.get("icon"),              # icon-folder 或 icon-music
            "batch": timestamp                     # 同一批次标识
        }))
    
    # 5. 批量插入数据库（每批500条，提高性能）
    TaskRecord.objects.bulk_create(bulk_set, batch_size=500)
    
    # 6. 启动异步刮削任务（不阻塞 API 响应）
    batch_auto_tag_task(timestamp, source_list, select_mode)
    
    return self.success_response()
```

**关键点**：
- 使用 `bulk_create` 批量插入，提高性能
- 生成时间戳作为批次标识，便于追踪和管理
- 异步启动任务，立即返回响应

---

### 2. 异步任务层

**文件位置**：[applications/task/tasks.py#L246](applications/task/tasks.py#L246)

**函数**：`batch_auto_tag_task`

**功能**：执行批量刮削任务，处理文件夹和文件

```python
def batch_auto_tag_task(batch, source_list, select_mode):
    """
    自动刮削任务（Celery 异步任务）
    
    参数：
        batch: 批次标识（时间戳）
        source_list: 数据源列表，如 ["migu", "qmusic", "netease"]
        select_mode: 匹配模式，"smart" 或 "simple"
    """
    # ========== 第一阶段：处理文件夹 ==========
    # 获取所有文件夹类型的任务记录
    folder_list = TaskRecord.objects.filter(batch=batch, icon="icon-folder").all()
    
    for folder in folder_list:
        # 扫描文件夹内容
        data = os.scandir(folder.full_path)
        bulk_set = []
        
        for entry in data:
            each = entry.name
            file_type = each.split(".")[-1]
            file_name = ".".join(each.split(".")[:-1])
            
            # 只处理音频文件
            if file_type not in ALLOW_TYPE:
                continue
            
            # 为文件夹内的每个文件创建任务记录
            bulk_set.append(TaskRecord(**{
                "batch": batch,
                "song_name": file_name,
                "full_path": f"{folder.full_path}/{each}",
                "icon": "icon-music",
            }))
        
        # 批量插入文件记录
        TaskRecord.objects.bulk_create(bulk_set)
    
    # ========== 第二阶段：刮削文件 ==========
    # 获取所有待处理的音乐文件（排除文件夹）
    task_list = TaskRecord.objects.filter(batch=batch).exclude(icon="icon-folder").all()
    
    # 逐个文件进行刮削
    for task in task_list:
        is_match = False
        
        # 按数据源顺序尝试匹配
        for resource in source_list:
            print("开始匹配", resource)
            try:
                # 调用匹配函数
                is_match = match_song(resource, task.full_path, select_mode)
            except Exception as e:
                print(e)
                is_match = False
                break  # 出错则停止当前文件
            
            # 如果匹配成功，更新任务状态
            if is_match:
                task.state = "success"
                task.save()
                
                # 创建或更新 Task 记录（用于前端显示）
                parent_path = os.path.dirname(task.full_path)
                Task.objects.update_or_create(full_path=task.full_path, defaults={
                    "state": task.state,
                    "parent_path": parent_path,
                    "filename": os.path.basename(task.full_path),
                    "song_name": task.song_name,
                    "artist_name": task.artist_name,
                })
                break  # 匹配成功，不再尝试其他数据源
        
        # 所有数据源都匹配失败
        if not is_match:
            task.state = "failed"
            task.save()
            parent_path = os.path.dirname(task.full_path)
            Task.objects.update_or_create(full_path=task.full_path, defaults={
                "state": task.state,
                "parent_path": parent_path,
                "filename": os.path.basename(task.full_path),
                "song_name": task.song_name,
                "artist_name": task.artist_name,
            })
```

**关键点**：
- 两阶段处理：先处理文件夹，再处理文件
- 按数据源优先级依次尝试
- 匹配成功后立即停止，不再尝试其他数据源
- 实时更新任务状态，便于前端显示进度

---

### 3. 核心匹配逻辑

**文件位置**：[applications/task/utils.py#L61](applications/task/utils.py#L61)

**函数**：`match_song`

**功能**：匹配歌曲并写入标签

```python
def match_song(resource, song_path, select_mode):
    """
    匹配歌曲并写入标签
    
    参数：
        resource: 数据源（netease, qmusic, migu, kugou等）
        song_path: 音乐文件路径
        select_mode: 匹配模式（"smart" 或 "simple"）
    
    返回：
        bool: 是否匹配成功
    """
    # ========== 第一步：读取本地文件信息 ==========
    file = music_tag.load_file(song_path)
    file_name = song_path.split("/")[-1]
    file_title = file_name.split('.')[0]
    
    # 获取本地标签信息（如果有的话）
    title = file["title"].value or file_title  # 优先使用标签中的标题
    artist = file["artist"].value or ""
    album = file["album"].value or ""
    
    # ========== 第二步：从数据源搜索 ==========
    songs = MusicResource(resource).fetch_id3_by_title(title)
    
    is_match = False
    song_select = None
    match_score_map = {
        "title": 0,    # 标题匹配分
        "artist": 0,    # 艺术家匹配分
        "album": 0,     # 专辑匹配分
    }
    
    # ========== 第三步：遍历搜索结果，计算匹配分数 ==========
    for song in songs:
        # 计算各项匹配分数
        match_score_map["title"] = match_score(title, song["name"])
        match_score_map["artist"] = match_artist(artist if artist else title, song["artist"])
        match_score_map["album"] = match_score(album if album else title, song["album"])
        
        # 如果本地有艺术家信息但匹配不上，扣分
        if artist and match_score_map["artist"] == 0:
            match_score_map["artist"] = -2
        
        # 特殊处理：标题包含艺术家信息
        if not artist and match_score_map["artist"] >= 1:
            if match_score_map["title"] >= 1:
                match_score_map["title"] = 2
        
        # ========== 第四步：判断是否匹配成功 ==========
        if sum(match_score_map.values()) >= 3:  # 智能模式：总分>=3
            is_match = True
            song_select = song
            break
        
        if select_mode == "simple":  # 简单模式：标题完全匹配
            if match_score_map["title"] == 2:
                is_match = True
                song_select = song
                break
    
    # ========== 第五步：匹配成功，写入标签 ==========
    if is_match:
        print(f"{title}>>>{song_select['name']}::{match_score_map}")
        song_select["filename"] = file_name
        song_select["file_full_path"] = song_path
        
        # 获取歌词
        song_select["lyrics"] = MusicResource(resource).fetch_lyric(song_select["id"])
        
        # 保存到文件
        save_music(file, song_select, False)
    
    return is_match
```

**关键点**：
- 优先使用本地标签信息，如果没有则使用文件名
- 智能模式综合评分，简单模式只看标题
- 匹配成功后自动获取歌词并写入

---

## 智能评分系统

### 评分规则

**文件位置**：[applications/task/utils.py#L34](applications/task/utils.py#L34)

```python
def match_score(my_value, u_value):
    """
    计算两个字符串的匹配分数
    
    参数：
        my_value: 本地值（文件中的标签）
        u_value: 网络值（从音乐平台获取的）
    
    返回：
        int: 匹配分数
            0 - 不匹配
            1 - 部分匹配（包含关系）
            2 - 完全匹配
    """
    # 1. 预处理：转小写、去空格
    my_value = my_value.lower().replace(" ", "")
    u_value = u_value.lower().replace(" ", "")
    
    # 2. 繁简转换（统一转为简体）
    if not issimp(my_value):
        my_value = convert(my_value, 'zh-cn')
    if not issimp(u_value):
        u_value = convert(u_value, 'zh-cn')
    
    # 3. 空值检查
    if not my_value or not u_value:
        return 0
    
    # 4. 完全匹配
    if my_value == u_value:
        return 2
    # 5. 包含匹配
    elif my_value in u_value or u_value in my_value:
        return 1
    # 6. 不匹配
    return 0
```

### 评分示例

| 本地值 | 网络值 | 预处理后 | 匹配类型 | 分数 |
|--------|--------|----------|----------|------|
| "周杰伦" | "周杰伦" | "周杰伦" vs "周杰伦" | 完全匹配 | 2 |
| "周杰伦" | "周杰伦-七里香" | "周杰伦" vs "周杰伦-七里香" | 包含匹配 | 1 |
| "周杰倫" | "周杰伦" | "周杰伦" vs "周杰伦" | 繁简转换后完全匹配 | 2 |
| "Jay Chou" | "jay chou" | "jaychou" vs "jaychou" | 完全匹配 | 2 |
| "周杰伦" | "林俊杰" | "周杰伦" vs "林俊杰" | 不匹配 | 0 |

### 艺术家匹配

**文件位置**：[applications/task/utils.py#L53](applications/task/utils.py#L53)

```python
def match_artist(my_value, u_value):
    """
    艺术家匹配（支持多艺术家）
    
    参数：
        my_value: 本地艺术家
        u_value: 网络艺术家（可能包含多个，用逗号分隔）
    
    返回：
        int: 匹配分数（累加多个艺术家的分数）
    """
    if "," in u_value:
        # 多个艺术家：分别匹配并累加分数
        return match_score(my_value, u_value.split(",")[0].replace(" ", "")) \
               + match_score(my_value, u_value.split(",")[1].replace(" ", ""))
    else:
        # 单个艺术家
        return match_score(my_value, u_value)
```

**示例**：
- 本地：`"周杰伦"`，网络：`"周杰伦,方文山"` → 匹配第一个艺术家 → 分数 2
- 本地：`"方文山"`，网络：`"周杰伦,方文山"` → 匹配第二个艺术家 → 分数 2

---

## 匹配模式

### 1. Smart 模式（智能匹配）

**特点**：
- 综合考虑标题、艺术家、专辑的匹配度
- 总分 >= 3 才算匹配成功
- 适合有部分标签信息的文件

**评分规则**：
```
总分 = title_score + artist_score + album_score

匹配条件：总分 >= 3

特殊规则：
1. 如果本地有艺术家但匹配不上，artist_score = -2（扣分）
2. 如果本地没有艺术家但标题包含艺术家信息，title_score = 2（加分）
```

**示例**：

| 场景 | title | artist | album | 总分 | 结果 |
|------|-------|--------|-------|------|------|
| 完全匹配 | 2 | 2 | 2 | 6 | ✅ 成功 |
| 部分匹配 | 1 | 1 | 1 | 3 | ✅ 成功 |
| 标题匹配 | 2 | 0 | 0 | 2 | ❌ 失败 |
| 艺术家不匹配 | 2 | -2 | 0 | 0 | ❌ 失败 |

### 2. Simple 模式（简单匹配）

**特点**：
- 只看标题匹配度
- 标题完全匹配（分数=2）就算成功
- 适合只有文件名的文件

**评分规则**：
```
匹配条件：title_score == 2（完全匹配）
```

**示例**：

| 场景 | title_score | 结果 |
|------|------------|------|
| "周杰伦" vs "周杰伦" | 2 | ✅ 成功 |
| "周杰伦" vs "周杰伦-七里香" | 1 | ❌ 失败 |
| "周杰倫" vs "周杰伦" | 2 | ✅ 成功（繁简转换） |

---

## 数据源说明

### 支持的音乐平台

**文件位置**：[applications/task/services/music_resource.py](applications/task/services/music_resource.py)

| 数据源 | 标识 | 类名 | 特点 |
|--------|------|------|------|
| 网易云音乐 | `netease` | `NetEaseMusicClient` | 数据丰富，搜索准确 |
| QQ 音乐 | `qmusic` | `QmusicClient` | 数据库大，更新快 |
| 咪咕音乐 | `migu` | `MiGuMusicClient` | 官方资源，质量高 |
| 酷狗音乐 | `kugou` | `KugouClient` | 歌词资源丰富 |
| 酷我音乐 | `kuwo` | `KuwoClient` | 老牌平台，数据全 |
| 声纹识别 | `acoustid` | `AcoustidClient` | 基于音频指纹，无需标签 |
| 智能标签 | `smart_tag` | `SmartTagClient` | 多平台综合匹配 |

### 数据源优先级

建议的优先级顺序：
```
1. netease（网易云音乐）- 数据最丰富
2. qmusic（QQ音乐）- 数据库最大
3. migu（咪咕音乐）- 官方资源
4. kugou（酷狗音乐）- 歌词资源
5. kuwo（酷我音乐）- 老牌平台
6. acoustid（声纹识别）- 无标签时使用
```

### 数据源接口

所有数据源都实现了统一的接口：

```python
class MusicResource:
    def __init__(self, info):
        self.resource = self.get_resource(info)
    
    def fetch_lyric(self, song_id):
        """获取歌词"""
        return self.resource.fetch_lyric(song_id)
    
    def fetch_id3_by_title(self, title):
        """根据标题搜索歌曲"""
        return self.resource.fetch_id3_by_title(title)
```

---

## 使用示例

### API 调用示例

**请求**：
```json
POST /api/batch_auto_update_id3/
Content-Type: application/json
Authorization: JWT <token>

{
  "file_full_path": "/path/to/music/folder",
  "select_data": [
    {
      "name": "song1.mp3",
      "icon": "icon-script-file"
    },
    {
      "name": "song2.mp3",
      "icon": "icon-script-file"
    },
    {
      "name": "album_folder",
      "icon": "icon-folder"
    }
  ],
  "music_info": {
    "select_mode": "smart",
    "source_list": ["netease", "qmusic", "migu", "kugou"]
  }
}
```

**响应**：
```json
{
  "code": 0,
  "msg": "success",
  "data": null
}
```

### Python 代码示例

```python
import requests

# 1. 获取 Token
response = requests.post('http://localhost:8002/api/token/', json={
    'username': 'admin',
    'password': 'admin'
})
token = response.json()['token']

# 2. 调用批量刮削 API
headers = {'Authorization': f'JWT {token}'}
response = requests.post(
    'http://localhost:8002/api/batch_auto_update_id3/',
    json={
        'file_full_path': '/path/to/music/folder',
        'select_data': [
            {'name': 'song.mp3', 'icon': 'icon-script-file'}
        ],
        'music_info': {
            'select_mode': 'smart',
            'source_list': ['netease', 'qmusic', 'migu']
        }
    },
    headers=headers
)

print(response.json())
# 输出: {"code": 0, "msg": "success", "data": null}
```

### JavaScript 代码示例

```javascript
// 1. 获取 Token
const tokenResponse = await fetch('http://localhost:8002/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'admin',
        password: 'admin'
    })
});
const { token } = await tokenResponse.json();

// 2. 调用批量刮削 API
const response = await fetch('http://localhost:8002/api/batch_auto_update_id3/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `JWT ${token}`
    },
    body: JSON.stringify({
        file_full_path: '/path/to/music/folder',
        select_data: [
            { name: 'song.mp3', icon: 'icon-script-file' }
        ],
        music_info: {
            select_mode: 'smart',
            source_list: ['netease', 'qmusic', 'migu']
        }
    })
});

const result = await response.json();
console.log(result);
```

---

## 数据模型

### TaskRecord 模型

**文件位置**：[applications/task/models.py#L15](applications/task/models.py#L15)

```python
class TaskRecord(models.Model):
    song_name = models.CharField(max_length=255, default="")      # 歌曲名称
    artist_name = models.CharField(max_length=255, default="")    # 艺术家名称
    full_path = models.CharField(max_length=255)                 # 文件完整路径
    tag_source = models.CharField(max_length=255, default="")   # 标签来源
    icon = models.CharField(max_length=255, default="icon-folder") # 图标类型
    state = models.CharField(max_length=255, default="wait")     # 任务状态
    extra = models.TextField(default="")                         # 额外信息
    created_at = models.DateTimeField(null=True, auto_now_add=True) # 创建时间
    batch = models.CharField(max_length=255, default="")        # 批次标识
```

**状态说明**：
- `wait`: 等待处理
- `success`: 刮削成功
- `failed`: 刮削失败

### Task 模型

**文件位置**：[applications/task/models.py#L4](applications/task/models.py#L4)

```python
class Task(models.Model):
    song_name = models.CharField(max_length=255, default="")      # 歌曲名称
    artist_name = models.CharField(max_length=255, default="")    # 艺术家名称
    full_path = models.CharField(max_length=255)                 # 文件完整路径
    state = models.CharField(max_length=255, default="wait")     # 任务状态
    parent_path = models.CharField(max_length=255, default="")   # 父目录路径
    filename = models.CharField(max_length=255, default="")      # 文件名
    created_at = models.DateTimeField(null=True, auto_now_add=True) # 创建时间
```

---

## 性能优化

### 1. 批量操作

```python
# 使用 bulk_create 批量插入，提高性能
TaskRecord.objects.bulk_create(bulk_set, batch_size=500)
```

### 2. 异步处理

```python
# 使用 Celery 异步任务，不阻塞 API
batch_auto_tag_task.delay(timestamp, source_list, select_mode)
```

### 3. 数据库索引

建议为以下字段添加索引：
```python
class TaskRecord(models.Model):
    batch = models.CharField(max_length=255, db_index=True)  # 批次索引
    state = models.CharField(max_length=255, db_index=True)  # 状态索引
    full_path = models.CharField(max_length=255, db_index=True)  # 路径索引
```

### 4. 并发控制

```python
# 使用线程池并发请求多个数据源
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as pool:
    results = pool.map(self.run, ["qmusic", "netease", "migu", "kugou"], [title] * 4)
```

---

## 注意事项

### 1. 文件权限

确保应用有读取和写入音乐文件的权限：
```bash
chmod -R 755 /path/to/music
```

### 2. 批量大小

建议每批不超过 500 个文件，避免内存溢出：
```python
TaskRecord.objects.bulk_create(bulk_set, batch_size=500)
```

### 3. 数据源限制

部分音乐平台可能有 API 调用频率限制，建议：
- 添加请求间隔
- 使用多个数据源轮换
- 实现请求重试机制

### 4. 网络超时

设置合理的超时时间：
```python
import requests

response = requests.get(url, timeout=10)  # 10秒超时
```

### 5. 错误处理

捕获并记录异常，避免单个文件失败影响整体：
```python
try:
    is_match = match_song(resource, task.full_path, select_mode)
except Exception as e:
    print(e)
    is_match = False
```

---

## 故障排查

### 问题 1：刮削全部失败

**可能原因**：
- 网络连接问题
- 数据源 API 变更
- 文件格式不支持

**解决方案**：
```python
# 检查网络连接
import requests
response = requests.get('https://music.163.com')
print(response.status_code)

# 检查支持的文件格式
from applications.task.constants import ALLOW_TYPE
print(ALLOW_TYPE)
```

### 问题 2：匹配不准确

**可能原因**：
- 文件名不规范
- 本地标签信息错误
- 匹配模式选择不当

**解决方案**：
```python
# 使用智能模式
music_info = {
    'select_mode': 'smart',  # 而不是 'simple'
    'source_list': ['netease', 'qmusic']
}

# 手动修正文件名
# 原文件名: "周杰伦-七里香.mp3"
# 修正后: "七里香.mp3"
```

### 问题 3：任务卡住

**可能原因**：
- Celery Worker 未启动
- 任务队列积压
- 数据库连接问题

**解决方案**：
```bash
# 检查 Celery Worker 状态
celery -A django_vue_cli inspect active

# 清除积压任务
curl -X GET http://localhost:8002/api/clear_celery/

# 重启 Celery Worker
supervisorctl restart celery_worker
```

---

## 扩展开发

### 添加新的数据源

**步骤 1**：实现数据源类

```python
# applications/task/services/newmusic.py
class NewMusicClient:
    BASE_URL = "https://api.newmusic.com/"
    
    def fetch_lyric(self, song_id):
        url = f"{self.BASE_URL}lyric?id={song_id}"
        res = requests.get(url)
        return res.json()["lyric"]
    
    def fetch_id3_by_title(self, title):
        url = f"{self.BASE_URL}search?q={title}"
        res = requests.get(url)
        songs = res.json()["songs"]
        # 转换为统一格式
        for song in songs:
            song["id"] = song["songId"]
            song["name"] = song["songName"]
            song["artist"] = song["singerName"]
            song["album"] = song["albumName"]
            song["album_img"] = song["coverUrl"]
            song["year"] = song["publishYear"]
        return songs
```

**步骤 2**：注册数据源

```python
# applications/task/services/music_resource.py
class MusicResource:
    def get_resource(self, info):
        if info == "netease":
            return NetEaseMusicClient()
        elif info == "newmusic":  # 新增
            return NewMusicClient()  # 新增
        # ...
```

**步骤 3**：使用新数据源

```python
{
  "music_info": {
    "select_mode": "smart",
    "source_list": ["netease", "newmusic"]  # 使用新数据源
  }
}
```

### 自定义匹配算法

```python
# applications/task/utils.py
def custom_match_score(my_value, u_value):
    """
    自定义匹配算法
    """
    # 实现自己的匹配逻辑
    # 例如：使用模糊匹配、编辑距离等
    pass

def match_song(resource, song_path, select_mode):
    # 使用自定义匹配算法
    match_score_map["title"] = custom_match_score(title, song["name"])
    # ...
```

---

## 总结

自动刮削功能是 Music Tag Web 的核心功能，通过以下关键技术实现：

1. **多数据源集成**：支持 6+ 个主流音乐平台
2. **智能匹配算法**：基于繁简转换、包含匹配的评分系统
3. **异步任务处理**：基于 Celery 的高性能异步处理
4. **批量操作优化**：使用 `bulk_create` 提高性能
5. **容错机制**：单个文件失败不影响其他文件
6. **实时状态跟踪**：实时更新任务状态

通过合理配置数据源和匹配模式，可以大大提高刮削的准确率和效率。
