from setuptools import setup

APP = ['main.py']
DATA_FILES = ['all_mcp_config.json']
OPTIONS = {
    'argv_emulation': False,
    'packages': ['PyQt6'],
    'includes': ['PyQt6.QtCore', 'PyQt6.QtWidgets'],
    'excludes': ['tkinter'],
    'plist': {
        'CFBundleName': 'MCP Server Switcher',
        'CFBundleDisplayName': 'MCP Server Switcher',
        'CFBundleGetInfoString': "MCP服务器配置编辑器",
        'CFBundleIdentifier': "com.mcp.serverswitcher",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': u"Copyright 2024, All Rights Reserved",
        'LSMinimumSystemVersion': '10.13',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
