#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テストランナー
全テストスイートの実行とカバレッジレポート生成
"""

import unittest
import sys
import os
from pathlib import Path

# テストディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def discover_and_run_tests(verbosity=2):
    """テスト自動発見・実行"""
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        stream=sys.stdout,
        buffer=True
    )
    
    result = runner.run(suite)
    return result


def run_specific_tests(test_modules=None, verbosity=2):
    """特定のテストモジュール実行"""
    if test_modules is None:
        test_modules = ['test_config', 'test_pdf_processing', 'test_gui']
    
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            suite.addTests(loader.loadTestsFromModule(module))
            print(f"✓ テストモジュール '{module_name}' を追加")
        except ImportError as e:
            print(f"⚠ テストモジュール '{module_name}' のインポートに失敗: {e}")
        except Exception as e:
            print(f"✗ テストモジュール '{module_name}' でエラー: {e}")
    
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        stream=sys.stdout,
        buffer=True
    )
    
    result = runner.run(suite)
    return result


def print_test_summary(result):
    """テスト結果サマリー表示"""
    print("\n" + "=" * 60)
    print("テスト実行結果サマリー")
    print("=" * 60)
    
    print(f"実行テスト数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    print(f"スキップ: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\n失敗したテスト ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nエラーが発生したテスト ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / 
                   max(result.testsRun, 1)) * 100
    print(f"\n成功率: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        print("✓ 全てのテストが成功しました")
        return True
    else:
        print("✗ 一部のテストが失敗しました")
        return False


def check_dependencies():
    """テスト実行に必要な依存関係チェック"""
    print("依存関係チェック:")
    
    dependencies = {
        'unittest': True,  # 標準ライブラリ
        'pathlib': True,   # 標準ライブラリ
        'json': True,      # 標準ライブラリ
        'tempfile': True,  # 標準ライブラリ
    }
    
    optional_dependencies = {
        'fitz': 'PyMuPDF (PDF処理)',
        'PIL': 'Pillow (画像処理)', 
        'reportlab': 'ReportLab (PDF生成)',
        'tkinter': 'tkinter (GUI)'
    }
    
    # 必須依存関係
    for dep, available in dependencies.items():
        status = "✓" if available else "✗"
        print(f"  {status} {dep}")
    
    # オプション依存関係
    print("\nオプション依存関係:")
    for dep, description in optional_dependencies.items():
        try:
            __import__(dep)
            print(f"  ✓ {dep} ({description})")
        except ImportError:
            print(f"  - {dep} ({description}) - 未インストール")
    
    print()


def main():
    """メイン実行関数"""
    print("🐊 AlligatorGar テストスイート")
    print("=" * 60)
    
    # コマンドライン引数処理
    import argparse
    parser = argparse.ArgumentParser(description='AlligatorGar テストスイート実行')
    parser.add_argument('-v', '--verbosity', type=int, default=2, 
                       choices=[0, 1, 2], help='テスト出力の詳細レベル')
    parser.add_argument('-m', '--modules', nargs='*', 
                       help='実行する特定のテストモジュール')
    parser.add_argument('-d', '--discover', action='store_true',
                       help='テスト自動発見を使用')
    parser.add_argument('--check-deps', action='store_true',
                       help='依存関係のみチェック')
    
    args = parser.parse_args()
    
    # 依存関係チェック
    if args.check_deps:
        check_dependencies()
        return
    
    check_dependencies()
    
    # テスト実行
    if args.discover:
        print("テスト自動発見モードで実行...")
        result = discover_and_run_tests(args.verbosity)
    else:
        print("指定モジュールテストモードで実行...")
        result = run_specific_tests(args.modules, args.verbosity)
    
    # 結果表示
    success = print_test_summary(result)
    
    # 終了コード
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()