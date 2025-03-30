import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidget, 
                           QTableWidgetItem, QVBoxLayout, QWidget, 
                           QPushButton, QDialog, QLineEdit, 
                           QLabel, QGridLayout, QMessageBox, QCheckBox,
                           QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class JsonEditorDialog(QDialog):
    def __init__(self, key="", command="", args=None, env=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑服务器配置")
        self.setModal(True)
        
        layout = QGridLayout()
        
        # Key input
        layout.addWidget(QLabel("服务器名称:"), 0, 0)
        self.key_input = QLineEdit(key)
        layout.addWidget(self.key_input, 0, 1)
        
        # Command input
        layout.addWidget(QLabel("命令:"), 1, 0)
        self.command_input = QLineEdit(command)
        layout.addWidget(self.command_input, 1, 1)
        
        # Args input
        layout.addWidget(QLabel("参数 (用逗号分隔):"), 2, 0)
        self.args_input = QLineEdit(",".join(args) if args else "")
        layout.addWidget(self.args_input, 2, 1)
        
        # Env input
        layout.addWidget(QLabel("环境变量 (key=value,key=value):"), 3, 0)
        env_str = ",".join([f"{k}={v}" for k, v in env.items()]) if env else ""
        self.env_input = QLineEdit(env_str)
        layout.addWidget(self.env_input, 3, 1)
        
        # Buttons
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        layout.addWidget(save_button, 4, 0)
        layout.addWidget(cancel_button, 4, 1)
        
        self.setLayout(layout)
    
    def get_data(self):
        args = [arg.strip() for arg in self.args_input.text().split(",") if arg.strip()]
        env = {}
        for env_pair in self.env_input.text().split(","):
            if "=" in env_pair:
                key, value = env_pair.split("=", 1)
                env[key.strip()] = value.strip()
        
        return {
            "key": self.key_input.text(),
            "command": self.command_input.text(),
            "args": args,
            "env": env
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCP服务器配置编辑器")
        self.setGeometry(100, 100, 800, 600)
        
        # 配置文件路径
        self.all_config_file = os.path.expanduser("~/.mcp_switcher/all_mcp_config.json")
        self.active_config_file = os.path.expanduser("~/.codeium/windsurf/mcp_config.json")
        
        # 创建系统托盘图标
        self.create_tray_icon()
        
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # 增加一列用于复选框
        self.table.setHorizontalHeaderLabels(["启用", "服务器名称", "命令", "参数", "环境变量"])
        layout.addWidget(self.table)
        
        # 添加按钮
        button_layout = QVBoxLayout()
        add_button = QPushButton("添加服务器")
        add_button.clicked.connect(self.add_server)
        edit_button = QPushButton("编辑服务器")
        edit_button.clicked.connect(self.edit_server)
        delete_button = QPushButton("删除服务器")
        delete_button.clicked.connect(self.delete_server)
        save_button = QPushButton("保存配置")
        save_button.clicked.connect(self.save_config)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)
        
        # 加载配置
        self.load_config()
    
    def create_checkbox_item(self, checked=False):
        item = QTableWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        return item
    
    def load_config(self):
        # 加载所有配置
        all_servers = {}
        if os.path.exists(self.all_config_file):
            try:
                with open(self.all_config_file, "r") as f:
                    all_servers = json.load(f).get("mcpServers", {})
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # 加载激活的配置
        active_servers = {}
        try:
            with open(self.active_config_file, "r") as f:
                active_servers = json.load(f).get("mcpServers", {})
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        
        # 合并配置，active_servers 优先
        merged_servers = all_servers.copy()
        merged_servers.update(active_servers)  # 使用 active_servers 覆盖同名配置
        
        # 更新表格
        self.table.setRowCount(len(merged_servers))
        for row, (key, value) in enumerate(merged_servers.items()):
            # 设置复选框
            is_active = key in active_servers
            self.table.setItem(row, 0, self.create_checkbox_item(is_active))
            
            # 设置其他列
            self.table.setItem(row, 1, QTableWidgetItem(key))
            self.table.setItem(row, 2, QTableWidgetItem(value.get("command", "")))
            self.table.setItem(row, 3, QTableWidgetItem(", ".join(value.get("args", []))))
            env_str = ", ".join([f"{k}={v}" for k, v in value.get("env", {}).items()])
            self.table.setItem(row, 4, QTableWidgetItem(env_str))
    
    def add_server(self):
        dialog = JsonEditorDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, self.create_checkbox_item(True))
            self.table.setItem(row, 1, QTableWidgetItem(data["key"]))
            self.table.setItem(row, 2, QTableWidgetItem(data["command"]))
            self.table.setItem(row, 3, QTableWidgetItem(", ".join(data["args"])))
            env_str = ", ".join([f"{k}={v}" for k, v in data["env"].items()])
            self.table.setItem(row, 4, QTableWidgetItem(env_str))
    
    def edit_server(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一个服务器")
            return
        
        key = self.table.item(current_row, 1).text()
        command = self.table.item(current_row, 2).text()
        args = [arg.strip() for arg in self.table.item(current_row, 3).text().split(",") if arg.strip()]
        env = {}
        for env_pair in self.table.item(current_row, 4).text().split(","):
            if "=" in env_pair:
                key_env, value = env_pair.split("=", 1)
                env[key_env.strip()] = value.strip()
        
        dialog = JsonEditorDialog(key, command, args, env, self)
        if dialog.exec():
            data = dialog.get_data()
            self.table.setItem(current_row, 1, QTableWidgetItem(data["key"]))
            self.table.setItem(current_row, 2, QTableWidgetItem(data["command"]))
            self.table.setItem(current_row, 3, QTableWidgetItem(", ".join(data["args"])))
            env_str = ", ".join([f"{k}={v}" for k, v in data["env"].items()])
            self.table.setItem(current_row, 4, QTableWidgetItem(env_str))
    
    def delete_server(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请先选择一个服务器")
            return
        
        reply = QMessageBox.question(self, "确认", "确定要删除这个服务器配置吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeRow(current_row)
    
    def save_config(self):
        all_config = {"mcpServers": {}}
        active_config = {"mcpServers": {}}
        
        for row in range(self.table.rowCount()):
            key = self.table.item(row, 1).text()
            command = self.table.item(row, 2).text()
            args = [arg.strip() for arg in self.table.item(row, 3).text().split(",") if arg.strip()]
            env_str = self.table.item(row, 4).text()
            env = {}
            for env_pair in env_str.split(","):
                if "=" in env_pair:
                    k, v = env_pair.split("=", 1)
                    env[k.strip()] = v.strip()
            
            is_active = self.table.item(row, 0).checkState() == Qt.CheckState.Checked
            
            server_config = {
                "command": command,
                "args": args,
                "env": env
            }
            
            # 保存到所有配置
            all_config["mcpServers"][key] = server_config
            
            # 如果被选中，也保存到激活配置
            if is_active:
                active_config["mcpServers"][key] = server_config
        
        try:
            # 确保激活配置文件的目录存在
            active_config_dir = os.path.dirname(self.active_config_file)
            if not os.path.exists(active_config_dir):
                os.makedirs(active_config_dir, exist_ok=True)
            
            # 保存所有配置
            if not os.path.exists(self.all_config_file):
                os.makedirs(os.path.dirname(self.all_config_file), exist_ok=True)
            
            # 保存激活配置
            with open(self.active_config_file, "w") as f:
                json.dump(active_config, f, indent=2)
            
            QMessageBox.information(self, "成功", "配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")
    
    def create_tray_icon(self):
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 设置图标
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
            # 设置应用程序图标
            app_icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon_.png")
            if os.path.exists(app_icon_path):
                self.setWindowIcon(QIcon(app_icon_path))
        else:
            # 如果找不到自定义图标，使用系统图标
            self.tray_icon.setIcon(QIcon.fromTheme("preferences-system"))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        show_action = tray_menu.addAction("显示")
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction("退出")
        quit_action.triggered.connect(QApplication.quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()  # 激活窗口
    
    def closeEvent(self, event):
        # 点击关闭按钮时最小化到托盘而不是退出
        event.ignore()
        self.hide()

def main():
    app = QApplication(sys.argv)
    # 确保应用程序不会在最后一个窗口关闭时退出
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
