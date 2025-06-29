#!/usr/bin/env python3
"""
Claude Desktop用攻撃結果送信サンプルスクリプト

Claude Desktopが攻撃結果を生成した後、
このスクリプトを使用して結果をアプリケーションに送信する。

使用例:
python scripts/send_attack_result.py "炎の剣が敵を貫く！" -50 0
"""

import sys
import requests
import json
import argparse
from typing import Optional

def send_attack_result(comment: str, defender_damage: int, attacker_damage: int = 0, server_url: str = "http://localhost:8000") -> bool:
    """
    攻撃結果をMCPエンドポイントに送信する
    
    Args:
        comment: 攻撃コメント
        defender_damage: 防御者へのダメージ（負の値）
        attacker_damage: 攻撃者へのダメージ（通常は0）
        server_url: アプリケーションサーバーのURL
        
    Returns:
        送信成功したかどうか
    """
    try:
        endpoint = f"{server_url}/api/mcp/results/attack"
        
        payload = {
            "comment": comment,
            "attacker": {
                "damage": attacker_damage
            },
            "defender": {
                "damage": defender_damage
            }
        }
        
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 攻撃結果送信成功: {result.get('message', '送信完了')}")
            print(f"   実行ID: {result.get('execution_id', 'N/A')}")
            return True
        else:
            print(f"❌ 攻撃結果送信失敗: HTTP {response.status_code}")
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
    parser = argparse.ArgumentParser(
        description="Claude Desktop用攻撃結果送信スクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python scripts/send_attack_result.py "炎の剣が敵を貫く！" -50
  python scripts/send_attack_result.py "氷の槍が炸裂！" -75 -10
  python scripts/send_attack_result.py "回復の光！" 30 20
        """
    )
    
    parser.add_argument("comment", help="攻撃の実況コメント")
    parser.add_argument("defender_damage", type=int, help="防御者へのダメージ（負の値でダメージ、正の値で回復）")
    parser.add_argument("attacker_damage", type=int, nargs='?', default=0, help="攻撃者へのダメージ（デフォルト: 0）")
    parser.add_argument("--server", default="http://localhost:8000", help="サーバーURL（デフォルト: http://localhost:8000）")
    
    args = parser.parse_args()
    
    print(f"攻撃結果を送信中:")
    print(f"  コメント: \"{args.comment}\"")
    print(f"  防御者ダメージ: {args.defender_damage}")
    print(f"  攻撃者ダメージ: {args.attacker_damage}")
    print(f"  送信先: {args.server}/api/mcp/results/attack")
    
    success = send_attack_result(args.comment, args.defender_damage, args.attacker_damage, args.server)
    
    if success:
        print("\n🎉 攻撃結果が正常に送信されました！")
        print("   フロントエンドで結果を確認してください。")
    else:
        print("\n💥 攻撃結果の送信に失敗しました。")
        print("   サーバーが起動しているか確認してください。")
        sys.exit(1)

if __name__ == "__main__":
    main()