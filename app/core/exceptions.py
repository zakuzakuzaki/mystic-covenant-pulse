"""共通例外クラス"""

class MysticCovenantException(Exception):
    """アプリケーション基底例外"""
    pass


class ClaudeDesktopError(MysticCovenantException):
    """Claude Desktop関連エラー"""
    pass


class SummonError(MysticCovenantException):
    """召喚処理関連エラー"""
    pass


class BattleError(MysticCovenantException):
    """バトル処理関連エラー"""
    pass


class MCPError(MysticCovenantException):
    """MCP処理関連エラー"""
    pass


class FileManagerError(MysticCovenantException):
    """ファイル管理関連エラー"""
    pass


class ConfigurationError(MysticCovenantException):
    """設定関連エラー"""
    pass