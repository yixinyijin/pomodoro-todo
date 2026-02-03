"""
更新提示对话框
"""
import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QProgressBar, QTextEdit, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QDesktopServices

from core.updater import Updater


class UpdateDialog(QDialog):
    """更新提示对话框"""

    update_downloaded = pyqtSignal(str)  # 下载完成信号

    def __init__(self, current_version: str, latest_version: str, changelog: str = "",
                 parent=None):
        """
        初始化更新对话框

        Args:
            current_version: 当前版本
            latest_version: 最新版本
            changelog: 更新日志
            parent: 父窗口
        """
        super().__init__(parent)
        self.current_version = current_version
        self.latest_version = latest_version
        self.changelog = changelog
        self.updater = Updater()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("发现新版本")
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # 图标和标题
        header_layout = QHBoxLayout()

        icon_label = QLabel()
        icon_label.setPixmap(self.style().standardIcon(
            self.style().SP_MessageBoxInformation).pixmap(48, 48))
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title_label = QLabel(f"发现新版本: v{self.latest_version}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title_label)

        version_label = QLabel(f"当前版本: v{self.current_version}")
        version_label.setStyleSheet("color: gray;")
        title_layout.addWidget(version_label)

        header_layout.addLayout(title_layout)
        layout.addLayout(header_layout)

        # 更新日志
        if self.changelog:
            changelog_label = QLabel("更新内容:")
            layout.addWidget(changelog_label)

            self.changelog_edit = QTextEdit()
            self.changelog_edit.setPlainText(self.changelog)
            self.changelog_edit.setReadOnly(True)
            self.changelog_edit.setMaximumHeight(150)
            layout.addWidget(self.changelog_edit)

        # 进度条 (初始隐藏)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 立即更新按钮
        self.update_btn = QPushButton("立即更新")
        self.update_btn.clicked.connect(self._start_update)
        button_layout.addWidget(self.update_btn)

        # 稍后更新按钮
        self.later_btn = QPushButton("稍后提醒我")
        self.later_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.later_btn)

        # 取消按钮
        self.cancel_btn = QPushButton("跳过此版本")
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self._skip_version)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def _start_update(self):
        """开始下载更新"""
        download_url = self.updater.get_download_url()
        if not download_url:
            self.status_label.setText("无法获取下载链接，请手动下载")
            self.update_btn.setEnabled(False)
            return

        # 禁用按钮
        self.update_btn.setEnabled(False)
        self.later_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("正在下载...")

        # 启动下载
        self._download_update(download_url)

    def _download_update(self, url: str):
        """下载更新"""
        try:
            import requests
            response = requests.get(url, stream=True, timeout=60)
            if response.status_code != 200:
                self.status_label.setText("下载失败")
                self._resetButtons()
                return

            total_size = int(response.headers.get('content-length', 0))
            self.progress_bar.setMaximum(100)

            import tempfile
            import os
            temp_dir = tempfile.mkdtemp()
            temp_exe = os.path.join(temp_dir, "PomodoroTodo_new.exe")

            downloaded = 0
            with open(temp_exe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int(downloaded * 100 / total_size)
                            self.progress_bar.setValue(percent)
                            self.status_label.setText(f"已下载 {downloaded // 1024} KB / {total_size // 1024} KB")

            self.status_label.setText("正在安装更新...")

            # 创建更新脚本
            exe_path = sys.executable
            exe_dir = os.path.dirname(exe_path)

            update_script = os.path.join(temp_dir, "update.bat")
            with open(update_script, 'w', encoding='utf-8') as f:
                f.write(f'''@echo off
echo 正在更新...
timeout /t 2 /nobreak >nul
del "{exe_path}" 2>nul
move "{temp_exe}" "{exe_path}" 2>nul
cd /d "{exe_dir}"
start "" "PomodoroTodo.exe"
''')

            # 启动更新脚本并退出
            import subprocess
            subprocess.Popen(
                ['cmd', '/c', update_script],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                detached=True
            )

            # 关闭当前应用
            self.accept()
            QApplication.quit()

        except Exception as e:
            self.status_label.setText(f"下载失败: {str(e)}")
            self._resetButtons()

    def _resetButtons(self):
        """重置按钮状态"""
        self.update_btn.setEnabled(True)
        self.later_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def _skip_version(self):
        """跳过此版本"""
        # 可以保存设置，标记跳过此版本
        self.reject()


class UpdateCheckDialog(QDialog):
    """检查更新对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.updater = Updater()
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("检查更新")
        self.setMinimumWidth(350)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # 标题
        title_label = QLabel("正在检查更新...")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 状态标签
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度
        layout.addWidget(self.progress_bar)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        # 启动检查
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._check_update)

    def _check_update(self):
        """执行更新检查"""
        try:
            is_new, latest_version = self.updater.check_update()
            if is_new:
                info = self.updater.get_version_info()
                self.accept()
                # 显示更新对话框
                from ui.styles import get_stylesheet, LIGHT_THEME
                dialog = UpdateDialog(
                    self.updater.current_version,
                    latest_version,
                    info.get('body', ''),
                    self.parent()
                )
                dialog.setStyleSheet(get_stylesheet(LIGHT_THEME))
                dialog.exec()
            else:
                self.status_label.setText("当前已是最新版本")
                self.progress_bar.setVisible(False)
                QTimer.singleShot(1500, self.accept)
        except Exception as e:
            self.status_label.setText(f"检查失败: {str(e)}")
            self.progress_bar.setVisible(False)
