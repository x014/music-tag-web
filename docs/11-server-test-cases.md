# 服务端测试用例文档

## 概述

本文档详细列出了 music-tag-web 项目服务端需要编写的测试用例，涵盖各个模块的单元测试和集成测试。

---

## 一、Music 模块测试用例

### 1.1 模型测试 (models.py)

#### 1.1.1 Album 模型测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| M-ALB-001 | 创建专辑基本字段 | 测试创建专辑时基本字段是否正确保存 | 无 | 1. 创建Album对象，设置name、song_count等字段<br>2. 保存到数据库<br>3. 查询验证 | 各字段值与设置值一致 |
| M-ALB-002 | 专辑关联艺术家 | 测试专辑与艺术家的外键关联 | 存在Artist对象 | 1. 创建Album并关联Artist<br>2. 保存并查询<br>3. 验证关联关系 | artist字段正确关联到指定Artist |
| M-ALB-003 | 专辑关联流派 | 测试专辑与流派的外键关联 | 存在Genre对象 | 1. 创建Album并关联Genre<br>2. 保存并查询 | genre字段正确关联到指定Genre |
| M-ALB-004 | 专辑关联封面附件 | 测试专辑与封面附件的关联 | 存在Attachment对象 | 1. 创建Album并设置attachment_cover<br>2. 保存并查询 | attachment_cover正确关联 |
| M-ALB-005 | 专辑字符串表示 | 测试__str__方法 | 无 | 1. 创建Album对象<br>2. 调用str()函数 | 返回专辑名称 |
| M-ALB-006 | 自动更新时间戳 | 测试updated_at字段自动更新 | 无 | 1. 创建Album对象<br>2. 修改字段并保存<br>3. 验证updated_at是否更新 | updated_at自动更新为当前时间 |

#### 1.1.2 Track 模型测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| M-TRK-001 | 创建歌曲基本字段 | 测试创建歌曲时基本字段保存 | 无 | 1. 创建Track对象，设置name、path、duration等<br>2. 保存并查询 | 各字段值正确 |
| M-TRK-002 | 歌曲关联专辑 | 测试歌曲与专辑的关联 | 存在Album对象 | 1. 创建Track并关联Album<br>2. 保存并验证 | album字段正确关联 |
| M-TRK-003 | 歌曲关联艺术家 | 测试歌曲与艺术家的关联 | 存在Artist对象 | 1. 创建Track并关联Artist<br>2. 保存并验证 | artist字段正确关联 |
| M-TRK-004 | 歌曲关联流派 | 测试歌曲与流派的关联 | 存在Genre对象 | 1. 创建Track并关联Genre<br>2. 保存并验证 | genre字段正确关联 |
| M-TRK-005 | 歌曲时长字段 | 测试duration字段 | 无 | 1. 创建Track设置duration为浮点数<br>2. 保存并查询 | duration值正确保存 |
| M-TRK-006 | 歌曲自动创建时间 | 测试created_at自动设置 | 无 | 1. 创建Track对象<br>2. 验证created_at | created_at自动设置为当前时间 |

#### 1.1.3 Artist 模型测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| M-ART-001 | 创建艺术家基本字段 | 测试创建艺术家 | 无 | 1. 创建Artist对象<br>2. 设置name、album_count等字段 | 各字段值正确 |
| M-ART-002 | 艺术家关联封面 | 测试艺术家封面附件关联 | 存在Attachment对象 | 1. 创建Artist并设置attachment_cover<br>2. 保存并验证 | attachment_cover正确关联 |
| M-ART-003 | 艺术家字符串表示 | 测试__str__方法 | 无 | 1. 创建Artist对象<br>2. 调用str()函数 | 返回艺术家名称 |

#### 1.1.4 Genre 模型测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| M-GEN-001 | 创建流派 | 测试创建流派 | 无 | 1. 创建Genre对象<br>2. 设置name字段 | name字段正确保存 |
| M-GEN-002 | 流派名称唯一性 | 测试name字段唯一约束 | 存在同名Genre | 1. 尝试创建同名Genre | 抛出IntegrityError异常 |

#### 1.1.5 Attachment 模型测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| M-ATT-001 | 创建附件 | 测试创建附件对象 | 准备测试图片文件 | 1. 创建Attachment对象<br>2. 上传图片文件 | 文件正确保存 |
| M-ATT-002 | 附件自动设置size | 测试save方法自动设置size | 准备测试图片 | 1. 创建Attachment并上传文件<br>2. 保存后验证size字段 | size字段自动设置为文件大小 |
| M-ATT-003 | 附件尺寸验证 | 测试ImageDimensionsValidator | 准备小于50x50的图片 | 1. 尝试上传过小图片 | 抛出ValidationError |
| M-ATT-004 | 附件扩展名验证 | 测试FileValidator扩展名检查 | 准备非图片文件 | 1. 尝试上传非允许扩展名文件 | 抛出ValidationError |
| M-ATT-005 | 附件大小限制验证 | 测试FileValidator大小限制 | 准备超过5MB的图片 | 1. 尝试上传超大文件 | 抛出ValidationError |

#### 1.1.6 Playlist 模型测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| M-PLY-001 | 创建播放列表 | 测试创建播放列表 | 存在User对象 | 1. 创建Playlist对象<br>2. 关联用户 | 播放列表正确创建 |
| M-PLY-002 | 播放列表隐私级别 | 测试privacy_level字段 | 无 | 1. 创建Playlist设置不同隐私级别<br>2. 验证choices有效性 | 隐私级别正确设置 |

#### 1.1.7 TrackFavorite 模型测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| M-FAV-001 | 创建收藏 | 测试创建歌曲收藏 | 存在User和Track | 1. 调用TrackFavorite.add方法 | 收藏正确创建 |
| M-FAV-002 | 收藏唯一性 | 测试同一用户收藏同一歌曲的唯一性 | 已存在收藏记录 | 1. 再次调用add方法 | 返回已存在记录，不重复创建 |
| M-FAV-003 | 收藏排序 | 测试按创建时间倒序排列 | 存在多个收藏 | 1. 查询收藏列表 | 按creation_date倒序排列 |

#### 1.1.8 Folder 模型测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| M-FLD-001 | 创建文件夹记录 | 测试创建Folder对象 | 无 | 1. 创建Folder对象<br>2. 设置path、name等字段 | 文件夹记录正确创建 |
| M-FLD-002 | UUID自动生成 | 测试uid字段自动生成 | 无 | 1. 创建Folder对象<br>2. 验证uid字段 | uid自动生成UUID |
| M-FLD-003 | 文件类型字段 | 测试file_type字段 | 无 | 1. 创建不同类型Folder<br>2. 设置file_type | file_type正确保存 |

### 1.2 验证器测试 (validators.py)

#### 1.2.1 ImageDimensionsValidator 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-IMG-001 | 最小宽度验证 | 测试min_width参数 | 准备测试图片 | 1. 设置min_width=100<br>2. 验证宽度小于100的图片 | 抛出ValidationError |
| V-IMG-002 | 最小高度验证 | 测试min_height参数 | 准备测试图片 | 1. 设置min_height=100<br>2. 验证高度小于100的图片 | 抛出ValidationError |
| V-IMG-003 | 最大宽度验证 | 测试max_width参数 | 准备测试图片 | 1. 设置max_width=1000<br>2. 验证宽度大于1000的图片 | 抛出ValidationError |
| V-IMG-004 | 最大高度验证 | 测试max_height参数 | 准备测试图片 | 1. 设置max_height=1000<br>2. 验证高度大于1000的图片 | 抛出ValidationError |
| V-IMG-005 | 精确宽度验证 | 测试width参数 | 准备测试图片 | 1. 设置width=200<br>2. 验证宽度不等于200的图片 | 抛出ValidationError |
| V-IMG-006 | 精确高度验证 | 测试height参数 | 准备测试图片 | 1. 设置height=200<br>2. 验证高度不等于200的图片 | 抛出ValidationError |
| V-IMG-007 | 合法图片通过 | 测试合法图片通过验证 | 准备符合要求的图片 | 1. 验证符合所有条件的图片 | 验证通过，无异常 |

#### 1.2.2 FileValidator 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-FILE-001 | 扩展名验证-合法 | 测试allowed_extensions合法扩展名 | 准备jpg文件 | 1. 设置allowed_extensions=['png','jpg']<br>2. 验证jpg文件 | 验证通过 |
| V-FILE-002 | 扩展名验证-非法 | 测试allowed_extensions非法扩展名 | 准备exe文件 | 1. 设置allowed_extensions=['png','jpg']<br>2. 验证exe文件 | 抛出ValidationError |
| V-FILE-003 | MIME类型验证-合法 | 测试allowed_mimetypes合法类型 | 准备图片文件 | 1. 设置allowed_mimetypes<br>2. 验证合法MIME类型 | 验证通过 |
| V-FILE-004 | MIME类型验证-非法 | 测试allowed_mimetypes非法类型 | 准备非图片文件 | 1. 设置allowed_mimetypes<br>2. 验证非法MIME类型 | 抛出ValidationError |
| V-FILE-005 | 最小文件大小验证 | 测试min_size参数 | 准备小文件 | 1. 设置min_size=1024<br>2. 验证小于1KB文件 | 抛出ValidationError |
| V-FILE-006 | 最大文件大小验证 | 测试max_size参数 | 准备大文件 | 1. 设置max_size=1024*1024<br>2. 验证大于1MB文件 | 抛出ValidationError |
| V-FILE-007 | 合法文件通过 | 测试符合所有条件的文件 | 准备合法文件 | 1. 验证符合所有条件的文件 | 验证通过 |

#### 1.2.3 DomainValidator 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-DOM-001 | 合法域名验证 | 测试合法域名 | 无 | 1. 验证"example.com" | 验证通过，返回原值 |
| V-DOM-002 | 非法域名验证 | 测试非法域名 | 无 | 1. 验证"invalid domain" | 抛出ValidationError |

### 1.3 工具函数测试 (utils.py)

#### 1.3.1 ChunkedPath 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| U-CP-001 | 文件名净化 | 测试sanitize_filename方法 | 无 | 1. 传入包含"/"的文件名<br>2. 调用sanitize_filename | "/"被替换为"-" |
| U-CP-002 | 保留文件名路径生成 | 测试preserve_file_name=True | 无 | 1. 创建ChunkedPath实例<br>2. 设置preserve_file_name=True<br>3. 生成路径 | 路径包含原始文件名 |
| U-CP-003 | 不保留文件名路径生成 | 测试preserve_file_name=False | 无 | 1. 创建ChunkedPath实例<br>2. 设置preserve_file_name=False<br>3. 生成路径 | 路径包含UUID文件名 |
| U-CP-004 | 路径分块结构 | 测试路径分块是否正确 | 无 | 1. 生成路径<br>2. 检查路径结构 | 路径包含root和分块目录 |

#### 1.3.2 strip_absolute_media_url 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| U-SAM-001 | HTTP URL替换 | 测试http开头的URL替换 | 配置MEDIA_URL | 1. 传入http开头的URL | URL被正确替换 |
| U-SAM-002 | HTTPS URL替换 | 测试https开头的URL替换 | 配置MEDIA_URL | 1. 传入https开头的URL | URL被正确替换 |
| U-SAM-003 | 非绝对URL不变 | 测试非绝对URL不处理 | 配置MEDIA_URL | 1. 传入相对路径 | 路径不变 |

#### 1.3.3 get_file_path_view 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| U-FPV-001 | Nginx代理路径 | 测试nginx类型的路径生成 | 设置REVERSE_PROXY_TYPE=nginx | 1. 传入音频文件路径<br>2. 调用函数 | 返回正确的nginx代理路径 |
| U-FPV-002 | Apache2代理路径 | 测试apache2类型的路径生成 | 设置REVERSE_PROXY_TYPE=apache2 | 1. 传入音频文件路径<br>2. 调用函数 | 返回正确的apache2代理路径 |
| U-FPV-003 | URL编码处理 | 测试包含特殊字符的路径 | 无 | 1. 传入包含%或?的路径 | 路径正确编码 |

---

## 二、Task 模块测试用例

### 2.1 模型测试 (models.py)

#### 2.1.1 Task 模型测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| T-TSK-001 | 创建任务记录 | 测试创建Task对象 | 无 | 1. 创建Task对象<br>2. 设置full_path、state等字段 | 任务记录正确创建 |
| T-TSK-002 | 默认状态值 | 测试state字段默认值 | 无 | 1. 创建Task不设置state<br>2. 验证state值 | state默认为"wait" |
| T-TSK-003 | 自动创建时间 | 测试created_at字段 | 无 | 1. 创建Task对象<br>2. 验证created_at | created_at自动设置 |

#### 2.1.2 TaskRecord 模型测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| T-TR-001 | 创建任务记录 | 测试创建TaskRecord对象 | 无 | 1. 创建TaskRecord对象<br>2. 设置各字段 | 记录正确创建 |
| T-TR-002 | 批次ID关联 | 测试batch字段 | 无 | 1. 创建TaskRecord设置batch<br>2. 按batch查询 | 正确关联和查询 |
| T-TR-003 | 匹配分数字段 | 测试match_score字段 | 无 | 1. 设置match_score为浮点数<br>2. 保存并验证 | 分数值正确保存 |

#### 2.1.3 BatchTask 模型测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| T-BT-001 | 创建批量任务 | 测试创建BatchTask对象 | 无 | 1. 创建BatchTask对象<br>2. 设置batch_id、task_type等 | 批量任务正确创建 |
| T-BT-002 | 进度百分比计算 | 测试progress_percent属性 | 无 | 1. 设置total_count=100, current_index=50<br>2. 获取progress_percent | 返回50.0 |
| T-BT-003 | 进度百分比-零总数 | 测试total_count=0时进度 | 无 | 1. 设置total_count=0<br>2. 获取progress_percent | 返回0 |
| T-BT-004 | 进度文本 | 测试progress_text属性 | 无 | 1. 设置total_count=100, current_index=50<br>2. 获取progress_text | 返回"50/100" |
| T-BT-005 | 状态选项验证 | 测试status字段choices | 无 | 1. 设置不同status值<br>2. 验证有效性 | 状态值正确设置 |
| T-BT-006 | 任务类型选项验证 | 测试task_type字段choices | 无 | 1. 设置不同task_type值<br>2. 验证有效性 | 任务类型正确设置 |
| T-BT-007 | batch_id唯一性 | 测试batch_id唯一约束 | 存在同batch_id记录 | 1. 尝试创建相同batch_id | 抛出IntegrityError |
| T-BT-008 | 按创建时间排序 | 测试默认排序 | 创建多个BatchTask | 1. 查询BatchTask列表 | 按created_at倒序排列 |

### 2.2 序列化器测试 (serialziers.py)

#### 2.2.1 FileListSerializer 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| S-FL-001 | 有效数据验证 | 测试有效输入数据 | 无 | 1. 传入有效file_path和sorted_fields<br>2. 验证is_valid | 验证通过 |
| S-FL-002 | 缺少file_path | 测试缺少必填字段 | 无 | 1. 不传file_path<br>2. 验证is_valid | 验证失败，返回错误 |
| S-FL-003 | 缺少sorted_fields | 测试缺少必填字段 | 无 | 1. 不传sorted_fields<br>2. 验证is_valid | 验证失败，返回错误 |

#### 2.2.2 Id3Serializer 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| S-ID3-001 | 有效数据验证 | 测试有效输入 | 无 | 1. 传入有效file_path和file_name | 验证通过 |
| S-ID3-002 | 缺少必填字段 | 测试缺少字段 | 无 | 1. 缺少file_name | 验证失败 |

#### 2.2.3 MusicId3Serializer 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| S-MID3-001 | 有效数据验证 | 测试完整有效数据 | 无 | 1. 传入所有必填字段 | 验证通过 |
| S-MID3-002 | 空值处理 | 测试allow_null和allow_blank | 无 | 1. 传入空字符串或null | 验证通过 |
| S-MID3-003 | 布尔字段验证 | 测试is_save_lyrics_file | 无 | 1. 传入非布尔值 | 验证失败 |
| S-MID3-004 | 缺少必填字段 | 测试缺少file_full_path | 无 | 1. 不传file_full_path | 验证失败 |

#### 2.2.4 UpdateId3Serializer 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| S-UID3-001 | 有效数据验证 | 测试有效music_id3_info列表 | 无 | 1. 传入包含多个MusicId3Serializer数据的列表 | 验证通过 |
| S-UID3-002 | 空列表验证 | 测试空列表 | 无 | 1. 传入空列表 | 根据业务逻辑验证 |

#### 2.2.5 FetchId3ByTitleSerializer 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| S-FIT-001 | 有效数据验证 | 测试必填字段 | 无 | 1. 传入title和resource | 验证通过 |
| S-FIT-002 | 可选字段处理 | 测试full_path可选 | 无 | 1. 不传full_path | 验证通过 |

#### 2.2.6 TaskSerializer 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| S-TSK-001 | 消息字段生成 | 测试get_message方法 | 创建Task对象 | 1. 序列化Task对象<br>2. 检查message字段 | 返回格式化的消息字符串 |
| S-TSK-002 | 文件存在检查 | 测试to_representation方法 | 创建Task对象 | 1. 序列化存在的文件路径<br>2. 检查is_exists字段 | is_exists为True |
| S-TSK-003 | 文件不存在处理 | 测试文件不存在时的处理 | 创建Task对象，路径不存在 | 1. 序列化不存在的文件路径<br>2. 检查is_exists字段 | is_exists为False，记录被删除 |

#### 2.2.7 BatchTaskSerializer 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| S-BT-001 | 只读字段 | 测试progress_percent和progress_text | 创建BatchTask对象 | 1. 序列化BatchTask<br>2. 检查只读字段 | 字段正确计算并返回 |

### 2.3 视图测试 (views.py)

#### 2.3.1 TaskViewSets.file_list 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-FL-001 | 正常获取文件列表 | 测试获取文件夹内容 | 存在测试文件夹 | 1. POST请求file_list<br>2. 传入有效file_path | 返回文件列表数据 |
| V-FL-002 | 文件夹不存在 | 测试不存在的路径 | 无 | 1. POST请求file_list<br>2. 传入不存在的路径 | 返回失败响应，提示文件夹不存在 |
| V-FL-003 | 按名称排序 | 测试sorted_fields包含name | 存在测试文件夹 | 1. POST请求sorted_fields=["name"] | 列表按名称排序 |
| V-FL-004 | 按更新时间排序 | 测试sorted_fields包含update_time | 存在测试文件夹 | 1. POST请求sorted_fields=["update_time"] | 列表按更新时间排序 |
| V-FL-005 | 按大小排序 | 测试sorted_fields包含size | 存在测试文件夹 | 1. POST请求sorted_fields=["size"] | 列表按大小排序 |
| V-FL-006 | 过滤非音乐文件 | 测试只返回允许类型 | 存在混合文件 | 1. POST请求file_list | 只返回ALLOW_TYPE中的文件类型 |
| V-FL-007 | 路径转换-容器路径 | 测试/app/media/路径转换 | 配置MEDIA_ROOT | 1. 传入/app/media/开头的路径 | 路径正确转换为MEDIA_ROOT |
| V-FL-008 | 关联任务状态 | 测试文件关联Task状态 | 存在Task记录 | 1. POST请求file_list | 返回的文件包含state字段 |

#### 2.3.2 TaskViewSets.music_id3 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-MID3-001 | 正常获取ID3信息 | 测试获取音乐文件ID3 | 存在测试音乐文件 | 1. POST请求music_id3<br>2. 传入有效文件路径和名称 | 返回ID3信息字典 |
| V-MID3-002 | 非音乐文件处理 | 测试lrc/txt文件 | 存在lrc文件 | 1. POST请求music_id3<br>2. 传入lrc文件 | 返回空数据 |
| V-MID3-003 | 文件读取异常 | 测试读取异常处理 | 无 | 1. POST请求music_id3<br>2. 传入无法读取的文件 | 返回失败响应 |
| V-MID3-004 | 路径转换 | 测试路径转换 | 配置MEDIA_ROOT | 1. 传入容器路径 | 路径正确转换 |

#### 2.3.3 TaskViewSets.update_id3 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-UID3-001 | 正常更新ID3 | 测试更新音乐文件ID3 | 存在测试音乐文件 | 1. POST请求update_id3<br>2. 传入有效music_id3_info | 返回成功响应 |
| V-UID3-002 | 批量更新 | 测试批量更新多个文件 | 存在多个测试文件 | 1. POST请求update_id3<br>2. 传入多个文件信息 | 所有文件更新成功 |

#### 2.3.4 TaskViewSets.batch_update_id3 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-BUID3-001 | 批量更新-文件 | 测试批量更新选中文件 | 存在测试文件 | 1. POST请求batch_update_id3<br>2. 选中多个文件 | 批量更新成功 |
| V-BUID3-002 | 批量更新-文件夹 | 测试批量更新文件夹内文件 | 存在测试文件夹 | 1. POST请求batch_update_id3<br>2. 选中文件夹 | 文件夹内所有音乐文件更新 |
| V-BUID3-003 | 路径转换 | 测试路径转换 | 配置MEDIA_ROOT | 1. 传入容器路径 | 路径正确转换 |

#### 2.3.5 TaskViewSets.batch_auto_update_id3 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-BAU-001 | 创建批量任务 | 测试创建自动刮削任务 | 存在测试文件 | 1. POST请求batch_auto_update_id3 | 返回batch_id，任务创建成功 |
| V-BAU-002 | TaskRecord创建 | 测试任务记录创建 | 无 | 1. 创建批量任务<br>2. 查询TaskRecord | TaskRecord正确创建 |
| V-BAU-003 | BatchTask创建 | 测试BatchTask创建 | 无 | 1. 创建批量任务<br>2. 查询BatchTask | BatchTask正确创建 |
| V-BAU-004 | Celery任务触发 | 测试异步任务触发 | Celery运行 | 1. 创建批量任务<br>2. 检查Celery任务 | 任务正确触发 |

#### 2.3.6 TaskViewSets.fetch_lyric 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-FLY-001 | 正常获取歌词 | 测试获取歌词 | Mock MusicResource | 1. POST请求fetch_lyric<br>2. 传入resource和song_id | 返回歌词内容 |
| V-FLY-002 | 歌词获取失败 | 测试获取歌词异常 | Mock异常情况 | 1. POST请求fetch_lyric<br>2. 模拟异常 | 返回错误提示信息 |

#### 2.3.7 TaskViewSets.fetch_id3_by_title 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-FIT-001 | 按标题搜索 | 测试按标题搜索ID3 | Mock MusicResource | 1. POST请求fetch_id3_by_title<br>2. 传入title和resource | 返回歌曲列表 |
| V-FIT-002 | acoustid资源 | 测试acoustid资源处理 | Mock MusicResource | 1. POST请求resource="acoustid" | 使用full_path作为title |
| V-FIT-003 | smart_tag资源 | 测试smart_tag资源处理 | Mock MusicResource | 1. POST请求resource="smart_tag" | 传入包含title和full_path的字典 |

#### 2.3.8 TaskViewSets.translation_lyc 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-TL-001 | 正常翻译歌词 | 测试歌词翻译 | Mock翻译服务 | 1. POST请求translation_lyc<br>2. 传入歌词内容 | 返回翻译后的歌词 |
| V-TL-002 | 空行处理 | 测试歌词中的空行 | 无 | 1. 传入包含空行的歌词 | 空行被正确处理 |
| V-TL-003 | 时间标签保留 | 测试保留时间标签 | 无 | 1. 传入带时间标签的歌词 | 时间标签被保留 |

#### 2.3.9 TaskViewSets.tidy_folder 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-TF-001 | 创建整理任务 | 测试创建文件夹整理任务 | 存在测试文件 | 1. POST请求tidy_folder | 返回batch_id，任务创建成功 |
| V-TF-002 | 一级目录整理 | 测试按一级目录整理 | 无 | 1. 设置first_dir参数 | 任务按指定字段整理 |
| V-TF-003 | 二级目录整理 | 测试按二级目录整理 | 无 | 1. 设置first_dir和second_dir | 任务按两级目录整理 |

#### 2.3.10 TaskViewSets.upload_image 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-UI-001 | 正常上传图片 | 测试上传图片 | 准备测试图片 | 1. POST请求upload_image<br>2. 上传图片文件 | 返回base64编码的图片数据 |
| V-UI-002 | 无效文件处理 | 测试上传非图片 | 无 | 1. POST请求upload_image<br>2. 上传非图片文件 | 返回验证错误 |

#### 2.3.11 TaskViewSets.batch_progress 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-BP-001 | 查询任务进度 | 测试查询批量任务进度 | 存在BatchTask | 1. GET请求batch_progress<br>2. 传入batch_id | 返回任务进度信息 |
| V-BP-002 | 缺少batch_id | 测试缺少参数 | 无 | 1. GET请求不传batch_id | 返回失败响应 |
| V-BP-003 | 任务不存在 | 测试不存在的任务 | 无 | 1. GET请求传入不存在的batch_id | 返回失败响应 |

#### 2.3.12 TaskViewSets.batch_list 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-BL-001 | 获取任务列表 | 测试获取批量任务列表 | 存在多个BatchTask | 1. GET请求batch_list | 返回任务列表 |
| V-BL-002 | 按类型过滤 | 测试task_type过滤 | 存在不同类型任务 | 1. GET请求batch_list?task_type=auto_tag | 返回指定类型任务 |
| V-BL-003 | 按状态过滤 | 测试status过滤 | 存在不同状态任务 | 1. GET请求batch_list?status=completed | 返回指定状态任务 |
| V-BL-004 | 数量限制 | 测试返回数量限制 | 存在超过20个任务 | 1. GET请求batch_list | 最多返回20条记录 |

#### 2.3.13 TaskViewSets.batch_cancel 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-BC-001 | 取消运行中任务 | 测试取消任务 | 存在pending/running状态任务 | 1. POST请求batch_cancel | 任务状态变为cancelled |
| V-BC-002 | 取消已完成任务 | 测试取消已结束任务 | 存在completed状态任务 | 1. POST请求batch_cancel | 返回失败，提示任务已结束 |
| V-BC-003 | 缺少batch_id | 测试缺少参数 | 无 | 1. POST请求不传batch_id | 返回失败响应 |

#### 2.3.14 TaskViewSets.batch_records 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-BR-001 | 获取任务记录 | 测试获取批量任务详细记录 | 存在TaskRecord | 1. GET请求batch_records | 返回任务记录列表 |
| V-BR-002 | 按状态过滤 | 测试state过滤 | 存在不同状态记录 | 1. GET请求batch_records?state=success | 返回指定状态记录 |
| V-BR-003 | 数量限制 | 测试返回数量限制 | 存在超过100条记录 | 1. GET请求batch_records | 最多返回100条记录 |

### 2.4 工具函数测试 (utils.py)

#### 2.4.1 timestamp_to_dt 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| U-TTD-001 | 正常转换 | 测试时间戳转日期时间 | 无 | 1. 传入有效时间戳 | 返回格式化的日期时间字符串 |
| U-TTD-002 | 自定义格式 | 测试自定义格式 | 无 | 1. 传入format_type参数 | 返回指定格式的日期时间 |

#### 2.4.2 folder_update_time 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| U-FUT-001 | 获取更新时间 | 测试获取文件夹更新时间 | 存在测试文件夹 | 1. 传入文件夹路径 | 返回datetime对象 |

#### 2.4.3 exists_dir 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| U-ED-001 | 存在目录 | 测试列表中存在目录 | 存在测试目录 | 1. 传入包含目录的列表 | 返回True |
| U-ED-002 | 不存在目录 | 测试列表中不存在目录 | 无 | 1. 传入不含目录的列表 | 返回False |

#### 2.4.4 match_score 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| U-MS-001 | 完全匹配 | 测试值完全相等 | 无 | 1. 传入相同的两个值 | 返回2 |
| U-MS-002 | 包含匹配 | 测试值包含关系 | 无 | 1. 传入包含关系的值 | 返回1 |
| U-MS-003 | 不匹配 | 测试值不匹配 | 无 | 1. 传入不匹配的值 | 返回0 |
| U-MS-004 | 大小写忽略 | 测试忽略大小写 | 无 | 1. 传入不同大小写的值 | 按忽略大小写匹配 |
| U-MS-005 | 空格忽略 | 测试忽略空格 | 无 | 1. 传入包含空格的值 | 按忽略空格匹配 |
| U-MS-006 | 繁简转换 | 测试繁简转换匹配 | 无 | 1. 传入繁简不同的值 | 自动转换后匹配 |
| U-MS-007 | 空值处理 | 测试空值情况 | 无 | 1. 传入空值 | 返回0 |

#### 2.4.5 match_artist 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| U-MA-001 | 单艺术家匹配 | 测试单个艺术家 | 无 | 1. 传入单个艺术家名 | 调用match_score |
| U-MA-002 | 多艺术家匹配 | 测试逗号分隔的多个艺术家 | 无 | 1. 传入"artist1,artist2" | 分别匹配并累加分数 |

#### 2.4.6 parse_filename 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| U-PF-001 | 带编号格式 | 测试"编号.艺术家-歌曲名"格式 | 无 | 1. 传入"3065.光良-童话" | 返回title="童话", artist="光良" |
| U-PF-002 | 艺术家-歌曲名格式 | 测试"艺术家-歌曲名"格式 | 无 | 1. 传入"李宗盛-山丘" | 返回title="山丘", artist="李宗盛" |
| U-PF-003 | 仅歌曲名格式 | 测试"歌曲名"格式 | 无 | 1. 传入"童话" | 返回title="童话", artist="" |
| U-PF-004 | 多个分隔符 | 测试多个"-"的情况 | 无 | 1. 传入"artist-song-name" | 只按第一个"-"分割 |

#### 2.4.7 detect_language 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| U-DL-001 | 中文检测 | 测试中文歌词 | 无 | 1. 传入中文歌词 | 返回"中文" |
| U-DL-002 | 英文检测 | 测试英文歌词 | 无 | 1. 传入英文歌词 | 返回"英文" |
| U-DL-003 | 日文检测 | 测试日文歌词 | 无 | 1. 传入日文歌词 | 返回"日文" |
| U-DL-004 | 韩文检测 | 测试韩文歌词 | 无 | 1. 传入韩文歌词 | 返回"韩文" |
| U-DL-005 | 泰文检测 | 测试泰文歌词 | 无 | 1. 传入泰文歌词 | 返回"泰文" |
| U-DL-006 | 混合语言 | 测试混合语言 | 无 | 1. 传入混合语言歌词 | 返回占比最高的语言 |
| U-DL-007 | 空歌词 | 测试空歌词 | 无 | 1. 传入空字符串 | 返回"未知" |

### 2.5 服务层测试 (services/)

#### 2.5.1 MusicIDS 测试 (music_ids.py)

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| S-MIDS-001 | 读取专辑名 | 测试album_name属性 | 准备测试音乐文件 | 1. 加载文件<br>2. 获取album_name | 返回专辑名或"未知专辑" |
| S-MIDS-002 | 读取艺术家 | 测试artist属性 | 准备测试音乐文件 | 1. 加载文件<br>2. 获取artist | 返回艺术家名 |
| S-MIDS-003 | 读取年份 | 测试year属性 | 准备测试音乐文件 | 1. 加载文件<br>2. 获取year | 返回年份整数 |
| S-MIDS-004 | 读取时长 | 测试duration属性 | 准备测试音乐文件 | 1. 加载文件<br>2. 获取duration | 返回时长（秒） |
| S-MIDS-005 | 读取比特率 | 测试bit_rate属性 | 准备测试音乐文件 | 1. 加载文件<br>2. 获取bit_rate | 返回比特率（kbps） |
| S-MIDS-006 | 读取封面 | 测试artwork属性 | 准备带封面的音乐文件 | 1. 加载文件<br>2. 获取artwork | 返回base64编码的封面 |
| S-MIDS-007 | 读取歌词 | 测试lyrics属性 | 准备带歌词的音乐文件 | 1. 加载文件<br>2. 获取lyrics | 返回歌词内容 |
| S-MIDS-008 | to_dict方法 | 测试完整信息输出 | 准备测试音乐文件 | 1. 加载文件<br>2. 调用to_dict | 返回包含所有信息的字典 |
| S-MIDS-009 | var_dict方法 | 测试变量字典输出 | 准备测试音乐文件 | 1. 加载文件<br>2. 调用var_dict | 返回模板变量字典 |
| S-MIDS-010 | 语言检测 | 测试language属性 | 准备带歌词的文件 | 1. 加载文件<br>2. 获取language | 返回检测到的语言 |

#### 2.5.2 MusicResource 测试 (music_resource.py)

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| S-MR-001 | 获取网易云音乐资源 | 测试netease资源 | Mock网络请求 | 1. 创建MusicResource("netease") | 返回NetEaseMusicClient实例 |
| S-MR-002 | 获取咪咕音乐资源 | 测试migu资源 | Mock网络请求 | 1. 创建MusicResource("migu") | 返回MiGuMusicClient实例 |
| S-MR-003 | 获取QQ音乐资源 | 测试qmusic资源 | Mock网络请求 | 1. 创建MusicResource("qmusic") | 返回QmusicClient实例 |
| S-MR-004 | 获取酷狗音乐资源 | 测试kugou资源 | Mock网络请求 | 1. 创建MusicResource("kugou") | 返回KugouClient实例 |
| S-MR-005 | 获取酷我音乐资源 | 测试kuwo资源 | Mock网络请求 | 1. 创建MusicResource("kuwo") | 返回KuwoClient实例 |
| S-MR-006 | 不支持的平台 | 测试不支持的平台 | 无 | 1. 创建MusicResource("unknown") | 抛出异常 |
| S-MR-007 | fetch_lyric方法 | 测试获取歌词 | Mock资源客户端 | 1. 调用fetch_lyric | 返回歌词内容 |
| S-MR-008 | fetch_id3_by_title方法 | 测试搜索歌曲 | Mock资源客户端 | 1. 调用fetch_id3_by_title | 返回歌曲列表 |

#### 2.5.3 update_music_info 测试 (update_ids.py)

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| S-UMI-001 | 更新基本信息 | 测试更新标题、艺术家等 | 准备测试音乐文件 | 1. 调用update_music_info<br>2. 传入基本信息 | 文件ID3信息更新成功 |
| S-UMI-002 | 更新歌词 | 测试更新歌词 | 准备测试音乐文件 | 1. 调用save_music<br>2. 传入lyrics | 歌词写入文件 |
| S-UMI-003 | 保存歌词文件 | 测试is_save_lyrics_file | 准备测试音乐文件 | 1. 设置is_save_lyrics_file=True | 生成.lrc文件 |
| S-UMI-004 | 更新封面 | 测试更新封面图片 | 准备测试音乐文件和图片 | 1. 传入album_img(base64) | 封面写入文件 |
| S-UMI-005 | 保存封面文件 | 测试is_save_album_cover | 准备测试音乐文件 | 1. 设置is_save_album_cover=True | 生成封面文件 |
| S-UMI-006 | URL封面下载 | 测试从URL下载封面 | Mock HTTP请求 | 1. 传入http开头的album_img | 下载并写入封面 |
| S-UMI-007 | 大封面压缩 | 测试大于5MB的封面压缩 | 准备大封面 | 1. 传入大于5MB的封面 | 自动压缩封面 |
| S-UMI-008 | 模板变量替换 | 测试包含${}的模板 | 准备测试音乐文件 | 1. 传入包含模板的值 | 变量正确替换 |
| S-UMI-009 | 文件重命名 | 测试filename字段 | 准备测试音乐文件 | 1. 传入新的filename | 文件被重命名 |
| S-UMI-010 | Task记录更新 | 测试Task记录创建/更新 | 无 | 1. 调用update_music_info | Task记录正确更新 |

### 2.6 Celery任务测试 (tasks.py)

#### 2.6.1 full_scan_folder 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| T-FSF-001 | 全量扫描 | 测试全量扫描文件夹 | 存在测试音乐目录 | 1. 调用full_scan_folder<br>2. 验证Folder记录 | Folder记录正确创建 |
| T-FSF-002 | 忽略路径 | 测试忽略指定路径 | 配置ignore_path | 1. 调用full_scan_folder | 忽略路径不被扫描 |
| T-FSF-003 | 音乐文件识别 | 测试识别音乐文件 | 存在多种格式文件 | 1. 调用full_scan_folder | file_type正确设置为music |
| T-FSF-004 | 图片文件识别 | 测试识别图片文件 | 存在封面图片 | 1. 调用full_scan_folder | file_type正确设置为image |
| T-FSF-005 | 批量创建优化 | 测试批量创建 | 存在大量文件 | 1. 调用full_scan_folder | 每500条批量创建一次 |

#### 2.6.2 batch_auto_tag_task 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| T-BAT-001 | 任务执行流程 | 测试完整执行流程 | 准备测试文件和TaskRecord | 1. 调用batch_auto_tag_task | 任务正确执行并更新状态 |
| T-BAT-002 | 文件夹展开 | 测试文件夹内文件展开 | 存在文件夹类型TaskRecord | 1. 执行任务 | 文件夹内文件被展开处理 |
| T-BAT-003 | 任务取消 | 测试任务取消功能 | 任务运行中 | 1. 设置status为cancelled | 任务停止执行 |
| T-BAT-004 | 成功计数 | 测试success_count更新 | Mock match_song返回True | 1. 执行任务 | success_count正确增加 |
| T-BAT-005 | 失败计数 | 测试failed_count更新 | Mock match_song返回False | 1. 执行任务 | failed_count正确增加 |
| T-BAT-006 | 进度更新 | 测试current_index更新 | 执行任务 | 1. 执行任务 | current_index正确更新 |
| T-BAT-007 | 异常处理 | 测试任务异常处理 | Mock异常 | 1. 模拟异常 | 任务状态变为failed |

#### 2.6.3 tidy_folder_task 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| T-TFT-001 | 一级目录整理 | 测试按一级目录整理 | 准备测试文件 | 1. 调用tidy_folder_task | 文件移动到正确目录 |
| T-TFT-002 | 二级目录整理 | 测试按二级目录整理 | 准备测试文件 | 1. 设置second_dir参数 | 文件移动到二级目录 |
| T-TFT-003 | 目录创建 | 测试自动创建目录 | 目标目录不存在 | 1. 执行整理任务 | 目录自动创建 |
| T-TFT-004 | 任务取消 | 测试任务取消 | 任务运行中 | 1. 设置status为cancelled | 任务停止执行 |
| T-TFT-005 | 异常处理 | 测试移动文件异常 | Mock异常 | 1. 模拟移动异常 | 创建失败TaskRecord |

---

## 三、User 模块测试用例

### 3.1 模型测试 (models.py)

#### 3.1.1 UserProfile 模型测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| U-UP-001 | 创建用户配置 | 测试创建UserProfile | 存在User对象 | 1. 创建UserProfile对象<br>2. 关联User | 配置正确创建 |
| U-UP-002 | 一对一关联 | 测试与User的一对一关系 | 存在User对象 | 1. 创建UserProfile<br>2. 通过User反向查询 | 正确关联 |
| U-UP-003 | subsonic_api_token | 测试API token字段 | 无 | 1. 设置subsonic_api_token<br>2. 保存并验证 | token正确保存 |

### 3.2 视图测试 (views.py)

#### 3.2.1 UserViewSets.info 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| V-UI-001 | 获取用户信息 | 测试获取当前用户信息 | 已登录用户 | 1. GET请求info接口 | 返回用户名和角色 |
| V-UI-002 | 管理员角色 | 测试管理员角色判断 | 已登录管理员 | 1. GET请求info接口 | role返回"admin" |
| V-UI-003 | 普通用户角色 | 测试普通用户角色判断 | 已登录普通用户 | 1. GET请求info接口 | role返回"other" |
| V-UI-004 | 未登录访问 | 测试未登录访问 | 未登录 | 1. GET请求info接口 | 返回401未授权 |

---

## 四、Subsonic 模块测试用例

### 4.1 视图测试 (views.py)

#### 4.1.1 SubsonicViewSet.ping 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-PING-001 | GET请求ping | 测试GET方式ping | 无 | 1. GET请求ping | 返回status=ok |
| SV-PING-002 | POST请求ping | 测试POST方式ping | 无 | 1. POST请求ping | 返回status=ok |
| SV-PING-003 | 无需认证 | 测试ping无需认证 | 未登录 | 1. 请求ping | 正常返回 |

#### 4.1.2 SubsonicViewSet.get_license 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-GL-001 | 获取许可证信息 | 测试获取许可证 | 无需认证 | 1. 请求getLicense | 返回许可证信息 |
| SV-GL-002 | 许可证有效期 | 测试有效期字段 | 无 | 1. 请求getLicense | licenseExpires为一年后 |

#### 4.1.3 SubsonicViewSet.get_artists 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-GA-001 | 获取艺术家列表 | 测试获取所有艺术家 | 已登录，存在Artist数据 | 1. 请求getArtists | 返回艺术家列表 |
| SV-GA-002 | 空列表处理 | 测试无艺术家时返回 | 已登录，无数据 | 1. 请求getArtists | 返回空列表 |

#### 4.1.4 SubsonicViewSet.get_cover_art 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-GCA-001 | 获取专辑封面 | 测试获取专辑封面 | 存在Album和Attachment | 1. 请求getCoverArt?id=al-1 | 返回封面图片响应 |
| SV-GCA-002 | 获取艺术家封面 | 测试获取艺术家封面 | 存在Artist和Attachment | 1. 请求getCoverArt?id=ar-1 | 返回封面图片响应 |
| SV-GCA-003 | 获取附件封面 | 测试获取附件封面 | 存在Attachment | 1. 请求getCoverArt?id=at-1 | 返回封面图片响应 |
| SV-GCA-004 | 缺少ID参数 | 测试缺少id参数 | 无 | 1. 请求getCoverArt不传id | 返回错误信息 |
| SV-GCA-005 | 无效ID格式 | 测试无效ID格式 | 无 | 1. 请求getCoverArt?id=invalid | 返回封面未找到错误 |
| SV-GCA-006 | 封面不存在 | 测试封面不存在 | Album无封面 | 1. 请求getCoverArt?id=al-xxx | 返回封面未找到错误 |

#### 4.1.5 SubsonicViewSet.get_artist 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-GART-001 | 获取艺术家详情 | 测试获取艺术家信息 | 已登录，存在Artist | 1. 请求getArtist?id=1 | 返回艺术家详情 |
| SV-GART-002 | 艺术家不存在 | 测试艺术家不存在 | 已登录 | 1. 请求getArtist?id=999 | 返回艺术家未找到错误 |

#### 4.1.6 SubsonicViewSet.get_song 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-GS-001 | 获取歌曲详情 | 测试获取歌曲信息 | 已登录，存在Track | 1. 请求getSong?id=1 | 返回歌曲详情 |
| SV-GS-002 | 歌曲不存在 | 测试歌曲不存在 | 已登录 | 1. 请求getSong?id=999 | 返回歌曲未找到错误 |

#### 4.1.7 SubsonicViewSet.get_album 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-GAL-001 | 获取专辑详情 | 测试获取专辑信息 | 已登录，存在Album | 1. 请求getAlbum?id=1 | 返回专辑详情 |
| SV-GAL-002 | 专辑不存在 | 测试专辑不存在 | 已登录 | 1. 请求getAlbum?id=999 | 返回专辑未找到错误 |

#### 4.1.8 SubsonicViewSet.stream 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-STR-001 | 流式播放 | 测试流式播放歌曲 | 已登录，存在Track | 1. 请求stream?id=1 | 返回音频流响应 |
| SV-STR-002 | 最大比特率限制 | 测试maxBitRate参数 | 已登录 | 1. 请求stream?id=1&maxBitRate=128 | 比特率被限制 |
| SV-STR-003 | 格式转换 | 测试format参数 | 已登录 | 1. 请求stream?id=1&format=mp3 | 返回指定格式 |
| SV-STR-004 | 原始格式 | 测试format=raw | 已登录 | 1. 请求stream?id=1&format=raw | 返回原始格式 |

#### 4.1.9 SubsonicViewSet.get_album_list2 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-AL2-001 | 按艺术家排序 | 测试alphabeticalByArtist | 已登录，存在Album | 1. 请求getAlbumList2?type=alphabeticalByArtist | 按艺术家名排序 |
| SV-AL2-002 | 随机排序 | 测试random类型 | 已登录，存在Album | 1. 请求getAlbumList2?type=random | 随机排序 |
| SV-AL2-003 | 按名称排序 | 测试alphabeticalByName | 已登录，存在Album | 1. 请求getAlbumList2?type=alphabeticalByName | 按专辑名排序 |
| SV-AL2-004 | 最近播放 | 测试recent类型 | 已登录，存在Album | 1. 请求getAlbumList2?type=recent | 按年份倒序 |
| SV-AL2-005 | 最新专辑 | 测试newest类型 | 已登录，存在Album | 1. 请求getAlbumList2?type=newest | 按创建时间倒序 |
| SV-AL2-006 | 播放最多 | 测试frequent类型 | 已登录，存在Album | 1. 请求getAlbumList2?type=frequent | 按播放量倒序 |
| SV-AL2-007 | 按流派筛选 | 测试byGenre类型 | 已登录，存在Album | 1. 请求getAlbumList2?type=byGenre&genre=Rock | 返回指定流派专辑 |
| SV-AL2-008 | 按年份筛选 | 测试byYear类型 | 已登录，存在Album | 1. 请求getAlbumList2?type=byYear&fromYear=2020&toYear=2023 | 返回指定年份范围专辑 |
| SV-AL2-009 | 分页参数 | 测试offset和size | 已登录 | 1. 请求getAlbumList2?offset=10&size=20 | 正确分页 |
| SV-AL2-010 | size上限 | 测试size最大值 | 已登录 | 1. 请求getAlbumList2?size=1000 | 最多返回500条 |

#### 4.1.10 SubsonicViewSet.star 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-STAR-001 | 收藏歌曲 | 测试收藏歌曲 | 已登录，存在Track | 1. 请求star?id=1 | 创建收藏记录 |
| SV-STAR-002 | 歌曲不存在 | 测试收藏不存在歌曲 | 已登录 | 1. 请求star?id=999 | 返回歌曲未找到错误 |

#### 4.1.11 SubsonicViewSet.unstar 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-UNSTAR-001 | 取消收藏 | 测试取消收藏 | 已登录，已收藏 | 1. 请求unstar?id=1 | 删除收藏记录 |
| SV-UNSTAR-002 | 歌曲不存在 | 测试取消收藏不存在歌曲 | 已登录 | 1. 请求unstar?id=999 | 返回歌曲未找到错误 |

#### 4.1.12 SubsonicViewSet.get_starred2 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-GS2-001 | 获取收藏列表 | 测试获取收藏歌曲 | 已登录，存在收藏 | 1. 请求getStarred2 | 返回收藏歌曲列表 |

#### 4.1.13 SubsonicViewSet.get_playlists 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-GP-001 | 获取播放列表 | 测试获取用户播放列表 | 已登录，存在Playlist | 1. 请求getPlaylists | 返回用户播放列表 |
| SV-GP-002 | 只返回自己的列表 | 测试只返回当前用户的列表 | 已登录，多用户数据 | 1. 请求getPlaylists | 只返回当前用户的列表 |

#### 4.1.14 异常处理测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SV-EX-001 | 认证失败处理 | 测试AuthenticationFailed异常 | 错误密码 | 1. 请求需要认证的接口 | 返回错误码40 |
| SV-EX-002 | 未认证处理 | 测试NotAuthenticated异常 | 未登录 | 1. 请求需要认证的接口 | 返回错误码10 |

### 4.2 工具函数测试 (utils.py)

#### 4.2.1 get_type_from_ext 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SU-GTE-001 | 获取MP3类型 | 测试mp3扩展名 | 无 | 1. 传入"song.mp3" | 返回audio/mpeg |
| SU-GTE-002 | 获取FLAC类型 | 测试flac扩展名 | 无 | 1. 传入"song.flac" | 返回audio/flac |
| SU-GTE-003 | 未知扩展名 | 测试未知扩展名 | 无 | 1. 传入"song.xyz" | 返回None |

#### 4.2.2 get_content_disposition 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SU-GCD-001 | 普通文件名 | 测试普通文件名 | 无 | 1. 传入"song.mp3" | 返回正确的Content-Disposition |
| SU-GCD-002 | 中文文件名 | 测试中文文件名 | 无 | 1. 传入"歌曲.mp3" | 正确URL编码 |
| SU-GCD-003 | 特殊字符文件名 | 测试包含特殊字符 | 无 | 1. 传入"song (1).mp3" | 正确URL编码 |

#### 4.2.3 handle_serve 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| SU-HS-001 | Nginx代理响应 | 测试nginx代理 | 配置REVERSE_PROXY_TYPE | 1. 调用handle_serve | 返回带X-Accel-Redirect头的响应 |
| SU-HS-002 | 更新访问时间 | 测试accessed_date更新 | 存在Track | 1. 调用handle_serve | Track的accessed_date被更新 |
| SU-HS-003 | 下载模式 | 测试download参数 | 无 | 1. 设置download=True | 响应包含Content-Disposition |

---

## 五、Utils 模块测试用例

### 5.1 翻译工具测试 (translation.py)

#### 5.1.1 translation_lyc_text 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| UT-TLT-001 | 短文本翻译 | 测试小于1000字符的翻译 | Mock翻译服务 | 1. 传入短文本 | 返回翻译结果 |
| UT-TLT-002 | 长文本分割翻译 | 测试大于1000字符的翻译 | Mock翻译服务 | 1. 传入长文本 | 分割后翻译并合并结果 |
| UT-TLT-003 | 按行分割 | 测试长文本按行分割 | 无 | 1. 传入包含换行的长文本 | 按行分割不超过1000字符 |

---

## 六、组件测试用例

### 6.1 DRF组件测试 (component/drf/)

#### 6.1.1 GenericViewSet 测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| C-GVS-001 | is_validated_data | 测试数据验证方法 | 无 | 1. 调用is_validated_data<br>2. 传入有效数据 | 返回validated_data |
| C-GVS-002 | 验证失败抛异常 | 测试验证失败 | 无 | 1. 调用is_validated_data<br>2. 传入无效数据 | 抛出ValidationError |
| C-GVS-003 | success_response | 测试成功响应 | 无 | 1. 调用success_response | 返回正确格式的成功响应 |
| C-GVS-004 | failure_response | 测试失败响应 | 无 | 1. 调用failure_response | 返回正确格式的失败响应 |
| C-GVS-005 | 分页信息计算 | 测试get_page_info | 无 | 1. 传入page和page_size | 返回正确的start和end |
| C-GVS-006 | 分页响应 | 测试my_paginated_response | 无 | 1. 调用my_paginated_response | 返回正确格式的分页响应 |

---

## 七、集成测试用例

### 7.1 完整刮削流程测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| I-FULL-001 | 完整刮削流程 | 测试从扫描到刮削的完整流程 | 准备测试音乐目录 | 1. 调用full_scan_folder<br>2. 调用batch_auto_tag_task<br>3. 验证结果 | 文件夹扫描、ID3更新、Task记录全部正确 |

### 7.2 API端到端测试

| 测试编号 | 测试名称 | 测试描述 | 前置条件 | 测试步骤 | 预期结果 |
|---------|---------|---------|---------|---------|---------|
| I-E2E-001 | 文件列表到ID3更新 | 测试完整操作流程 | 准备测试文件 | 1. 获取文件列表<br>2. 获取ID3信息<br>3. 更新ID3 | 所有操作成功完成 |
| I-E2E-002 | 批量刮削流程 | 测试批量自动刮削 | 准备测试文件 | 1. 创建批量任务<br>2. 查询进度<br>3. 验证结果 | 任务正确执行并返回结果 |

---

## 八、测试覆盖率目标

| 模块 | 目标覆盖率 | 优先级 |
|-----|----------|-------|
| applications/music/models.py | 90% | 高 |
| applications/music/validators.py | 95% | 高 |
| applications/music/utils.py | 85% | 中 |
| applications/task/models.py | 90% | 高 |
| applications/task/views.py | 80% | 高 |
| applications/task/serialziers.py | 90% | 高 |
| applications/task/utils.py | 85% | 高 |
| applications/task/services/ | 75% | 中 |
| applications/task/tasks.py | 70% | 中 |
| applications/user/models.py | 90% | 高 |
| applications/user/views.py | 85% | 高 |
| applications/subsonic/views.py | 75% | 中 |
| applications/subsonic/utils.py | 85% | 中 |
| applications/utils/translation.py | 80% | 中 |
| component/drf/viewsets.py | 90% | 高 |

---

## 九、测试环境配置建议

### 9.1 测试依赖

```python
# requirements/test.txt
pytest>=7.0.0
pytest-django>=4.5.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
factory-boy>=3.2.0
faker>=18.0.0
responses>=0.23.0  # Mock HTTP请求
celery[testing]>=5.3.0  # Celery测试支持
```

### 9.2 pytest配置示例

```python
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = django_vue_cli.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=applications --cov=component --cov-report=html --cov-report=term
```

### 9.3 测试基类示例

```python
# applications/conftest.py
import pytest
from django.contrib.auth.models import User

@pytest.fixture
def test_user():
    return User.objects.create_user(
        username='testuser',
        password='testpass123'
    )

@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@test.com'
    )
```

---

## 十、测试执行命令

```bash
# 运行所有测试
pytest

# 运行指定模块测试
pytest applications/music/tests/

# 运行指定测试文件
pytest applications/task/tests/test_views.py

# 运行指定测试用例
pytest applications/task/tests/test_views.py::TestTaskViewSets::test_file_list

# 生成覆盖率报告
pytest --cov=applications --cov-report=html

# 运行标记的测试
pytest -m "integration"
```

---

## 十一、测试用例统计

| 模块 | 测试用例数量 |
|-----|------------|
| Music 模块 | 52 |
| Task 模块 | 98 |
| User 模块 | 7 |
| Subsonic 模块 | 42 |
| Utils 模块 | 3 |
| 组件测试 | 6 |
| 集成测试 | 2 |
| **总计** | **210** |

---

*文档生成时间: 2026-03-15*
