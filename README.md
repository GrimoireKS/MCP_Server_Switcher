# MCP Server Switcher

MCP Server Switcher是一个用于管理和切换MCP服务器配置的图形界面工具。

## 功能特点

- 管理多个MCP服务器配置
- 通过勾选框轻松启用/禁用特定服务器
- 编辑服务器配置（名称、命令、参数和环境变量）
- 系统托盘集成，方便快速访问
- 自动保存配置到用户目录

## 使用方法

1. 启动应用程序
2. 添加、编辑或删除服务器配置
3. 勾选要启用的服务器
4. 点击"保存配置"应用更改

配置文件保存在：
- 所有配置：`~/.mcp_switcher/all_mcp_config.json`
- 当前激活配置：`~/.codeium/windsurf/mcp_config.json`

## 技术栈

- Python
- PyQt6（GUI框架）
- JSON（配置文件格式）

## 开发说明

此应用程序使用PyInstaller打包为可执行文件。

### 打包命令

```bash
pyinstaller --name="MCP Server Switcher" --windowed --icon=resources/icon_.png --add-data="all_mcp_config.json:." --add-data="resources/*.png:resources" main.py
```

## 声明

所有代码和资源均由AI模型（Claude 3.5 Sonnet、Claude 3.7 Sonnet和GPT-4o）生成。

## 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。
