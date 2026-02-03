"""
自动更新模块 - 基于 GitHub Releases
"""
import requests
import os
import sys
import subprocess
import shutil
import tempfile
from packaging import version

# GitHub 配置 - 需要根据实际仓库修改
GITHUB_OWNER = "your_username"
GITHUB_REPO = "pomodoro_todo"


class Updater:
    """GitHub Releases 自动更新器"""

    def __init__(self, owner: str = None, repo: str = None, current_version: str = None):
        self.owner = owner or GITHUB_OWNER
        self.repo = repo or GITHUB_REPO
        self.current_version = current_version or "1.0.0"
        self.api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"
        self.headers = {"Accept": "application/vnd.github.v3+json"}

    def check_update(self) -> tuple[bool, str]:
        """
        检查是否有新版本

        Returns:
            tuple: (是否有新版本, 最新版本号)
        """
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                latest = response.json()
                latest_version = latest.get('tag_name', '').lstrip('v')
                is_new = version.parse(latest_version) > version.parse(self.current_version)
                return is_new, latest_version
            elif response.status_code == 404:
                # 仓库或 release 不存在
                return False, ""
        except requests.RequestException:
            pass
        return False, ""

    def get_download_url(self) -> str:
        """
        获取最新版本下载链接

        Returns:
            str: exe 文件下载链接，失败返回空字符串
        """
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                latest = response.json()
                assets = latest.get('assets', [])
                for asset in assets:
                    if asset.get('name', '').endswith('.exe'):
                        return asset.get('browser_download_url', '')
                # 如果没有 assets，返回 source tarball
                return latest.get('html_url', '') + '/download'
        except requests.RequestException:
            pass
        return ""

    def download_and_install(self, latest_url: str) -> bool:
        """
        下载并安装新版本

        Args:
            latest_url: 新版本下载链接

        Returns:
            bool: 是否成功启动更新
        """
        temp_dir = tempfile.mkdtemp()
        exe_path = sys.executable
        exe_dir = os.path.dirname(exe_path)

        try:
            # 下载新版本
            response = requests.get(latest_url, stream=True, timeout=60)
            if response.status_code != 200:
                return False

            temp_exe = os.path.join(temp_dir, "PomodoroTodo_new.exe")
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(temp_exe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

            # 创建更新脚本 (bat 文件)
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

            # 启动更新脚本并退出当前程序
            subprocess.Popen(
                ['cmd', '/c', update_script],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                detached=True
            )
            return True

        except Exception:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

    def get_version_info(self) -> dict:
        """
        获取最新版本信息

        Returns:
            dict: 版本信息字典
        """
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                latest = response.json()
                return {
                    'version': latest.get('tag_name', '').lstrip('v'),
                    'name': latest.get('name', ''),
                    'body': latest.get('body', ''),
                    'html_url': latest.get('html_url', ''),
                    'published_at': latest.get('published_at', ''),
                }
        except requests.RequestException:
            pass
        return {}
