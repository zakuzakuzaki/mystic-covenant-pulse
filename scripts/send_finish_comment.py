#!/usr/bin/env python3
"""
Claude Desktop用決着コメント送信サンプルスクリプト

Claude Desktopが決着コメントを生成した後、
このスクリプトを使用してコメントをアプリケーションに送信する。

使用例:
python scripts/send_finish_comment.py "勝利の光よ、全てを照らせ！"
"""

import sys
import requests
import json
from typing import Optional

def send_finish_comment(comment: str, server_url: str = "http://localhost:8000") -> bool:
    """
    決着コメントをMCPエンドポイントに送信する
    
    Args:
        comment: 決着コメント
        server_url: アプリケーションサーバーのURL
        
    Returns:
        送信成功したかどうか
    """
    try:
        endpoint = f"{server_url}/api/mcp/results/finish"
        
        payload = {
            "comment": comment
        }
        
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 決着コメント送信成功: {result.get('message', '送信完了')}")
            print(f"   実行ID: {result.get('execution_id', 'N/A')}")
            return True
        else:
            print(f"❌ 決着コメント送信失敗: HTTP {response.status_code}")
            print(f"   レスポンス: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 通信エラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python scripts/send_finish_comment.py \"決着コメント\"")
        print("\n例:")
        print("  python scripts/send_finish_comment.py \"勝利の光よ、全てを照らせ！\"")
        sys.exit(1)
    
    comment = sys.argv[1]
    server_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    print(f"決着コメントを送信中: \"{comment}\"")
    print(f"送信先: {server_url}/api/mcp/results/finish")
    
    success = send_finish_comment(comment, server_url)
    
    if success:
        print("\n🎉 決着コメントが正常に送信されました！")
        print("   フロントエンドで結果を確認してください。")
    else:
        print("\n💥 決着コメントの送信に失敗しました。")
        print("   サーバーが起動しているか確認してください。")
        sys.exit(1)

if __name__ == "__main__":
    main()