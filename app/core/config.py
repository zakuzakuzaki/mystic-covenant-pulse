"""アプリケーション設定"""

from pathlib import Path
import json
from typing import Dict, Any, Optional

class Settings:
    """アプリケーション設定クラス"""
    
    def __init__(self):
        """設定初期化"""
        # ディレクトリ設定
        self.CONFIG_DIR = Path("config")
        self.STATIC_DIR = Path("static")
        self.ASSETS_DIR = Path("assets")
        
        # 必要なディレクトリを作成
        self.ASSETS_DIR.mkdir(exist_ok=True)
        self.CONFIG_DIR.mkdir(exist_ok=True)
        self.STATIC_DIR.mkdir(exist_ok=True)
        
        # 設定ファイルを読み込み
        self._load_config()
    
    def _load_config(self):
        """設定ファイルを読み込む"""
        config_file = self.CONFIG_DIR / "app_config.json"
        
        # デフォルト設定
        default_config = {
            "app": {
                "name": "召喚獣バトルAPI",
                "version": "0.1.0",
                "description": "召喚呪文から3D召喚獣を生成してバトルするAPI"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": True
            },
            "cors": {
                "allow_origins": ["*"],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"]
            }
        }
        
        # 設定ファイルが存在する場合は読み込み、なければデフォルトを作成
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = default_config
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        
        # 設定を属性に展開
        self.APP_NAME = config["app"]["name"]
        self.APP_VERSION = config["app"]["version"] 
        self.APP_DESCRIPTION = config["app"]["description"]
        
        self.HOST = config["server"]["host"]
        self.PORT = config["server"]["port"]
        self.DEBUG = config["server"]["debug"]
        
        self.ALLOW_ORIGINS = config["cors"]["allow_origins"]
        self.ALLOW_CREDENTIALS = config["cors"]["allow_credentials"]
        self.ALLOW_METHODS = config["cors"]["allow_methods"]
        self.ALLOW_HEADERS = config["cors"]["allow_headers"]
        
        # Claude Desktop設定ファイルパス
        self.CLAUDE_CONFIG_FILE = self.CONFIG_DIR / "claude_desktop_config.json"

# グローバル設定インスタンス
settings = Settings()