# VSCode 终端自动激活 Python 虚拟环境配置

## 问题描述

项目需要使用 Python 3.9，但系统默认 Python 版本是 3.11。需要在打开新终端时自动激活项目的 venv 虚拟环境。

## 解决方案

在项目根目录创建 `.vscode/settings.json` 文件，配置终端自动激活虚拟环境。

### 配置文件内容

```json
{
    "python.defaultInterpreterPath": "d:\\code\\github\\music-tag-web\\venv\\Scripts\\python.exe",
    "python.terminal.activateEnvironment": true,
    "terminal.integrated.profiles.windows": {
        "PowerShell": {
            "source": "PowerShell",
            "args": [
                "-NoExit",
                "-Command",
                "& 'd:\\code\\github\\music-tag-web\\venv\\Scripts\\Activate.ps1'"
            ]
        }
    },
    "terminal.integrated.defaultProfile.windows": "PowerShell"
}
```

### 配置说明

| 配置项 | 说明 |
|--------|------|
| `python.defaultInterpreterPath` | 指定默认 Python 解释器路径（使用绝对路径） |
| `python.terminal.activateEnvironment` | 允许终端自动激活 Python 环境 |
| `terminal.integrated.profiles.windows` | 自定义终端配置，在启动时自动执行激活脚本 |
| `terminal.integrated.defaultProfile.windows` | 设置默认终端为 PowerShell |

## 使用步骤

1. **重新加载 VSCode 窗口**
   - 按 `Ctrl+Shift+P`
   - 输入 `Reload Window` 并回车

2. **选择 Python 解释器**
   - 按 `Ctrl+Shift+P`
   - 输入 `Python: Select Interpreter`
   - 选择 `venv\Scripts\python.exe` (Python 3.9.x)

3. **打开新终端**
   - 关闭所有现有终端
   - 按 `` Ctrl+` `` 打开新终端
   - 终端应显示 `(venv)` 前缀，表示虚拟环境已激活

## 验证

在新终端中执行：

```powershell
python --version
```

应显示 `Python 3.9.x`（虚拟环境中的版本），而非系统默认版本。

## 注意事项

- 配置文件中的路径使用绝对路径，确保 VSCode 能正确找到虚拟环境
- 如果项目路径变更，需要更新 `settings.json` 中的路径
- 此配置仅对当前项目生效，不会影响其他项目
