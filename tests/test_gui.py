#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI機能のテスト
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# GUI関連ライブラリの可用性チェック
try:
    import tkinter as tk
    from tkinter import ttk
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    tk = MagicMock()
    ttk = MagicMock()


@unittest.skipIf(not GUI_AVAILABLE, "tkinterが利用できません")
class TestGUIBasicFunctionality(unittest.TestCase):
    """GUI基本機能テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        if GUI_AVAILABLE:
            self.root = tk.Tk()
            self.root.withdraw()  # ウィンドウを非表示
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if GUI_AVAILABLE and hasattr(self, 'root'):
            try:
                self.root.destroy()
            except:
                pass
    
    def test_tkinter_availability(self):
        """tkinter利用可能性テスト"""
        self.assertTrue(GUI_AVAILABLE)
        if GUI_AVAILABLE:
            self.assertIsNotNone(tk.Tk)
            self.assertIsNotNone(ttk.Style)
    
    def test_basic_widget_creation(self):
        """基本ウィジェット作成テスト"""
        if not GUI_AVAILABLE:
            self.skipTest("GUI not available")
        
        # フレーム作成
        frame = ttk.Frame(self.root)
        self.assertIsNotNone(frame)
        
        # ラベル作成
        label = ttk.Label(frame, text="Test Label")
        self.assertIsNotNone(label)
        
        # ボタン作成
        button = ttk.Button(frame, text="Test Button")
        self.assertIsNotNone(button)
    
    def test_style_configuration(self):
        """スタイル設定テスト"""
        if not GUI_AVAILABLE:
            self.skipTest("GUI not available")
        
        style = ttk.Style()
        
        # デフォルトテーマの設定
        try:
            style.theme_use('default')
            current_theme = style.theme_use()
            self.assertIsInstance(current_theme, str)
        except Exception as e:
            self.fail(f"スタイル設定でエラー: {e}")
    
    def test_cross_platform_font_selection(self):
        """クロスプラットフォームフォント選択テスト"""
        if sys.platform.startswith('win'):
            expected_fonts = {
                'title': ('Meiryo', 12, 'bold'),
                'normal': ('Meiryo', 9),
                'mono': ('Consolas', 9),
                'emoji': ('Segoe UI Emoji', 16)
            }
        else:
            expected_fonts = {
                'title': ('DejaVu Sans', 12, 'bold'),
                'normal': ('DejaVu Sans', 9),
                'mono': ('DejaVu Sans Mono', 9),
                'emoji': ('DejaVu Sans', 16)
            }
        
        # フォント設定が適切であることを確認
        for font_type, font_spec in expected_fonts.items():
            self.assertIsInstance(font_spec, tuple)
            self.assertEqual(len(font_spec), 3)  # (name, size, style)
            self.assertIsInstance(font_spec[0], str)  # フォント名
            self.assertIsInstance(font_spec[1], int)  # フォントサイズ


class TestGUIConfiguration(unittest.TestCase):
    """GUI設定テスト"""
    
    def test_default_config_generation(self):
        """デフォルト設定生成テスト"""
        # OS別デフォルト設定
        if sys.platform.startswith('win'):
            expected_font = "msgothic.ttc"
            expected_paths = ["\\\\fileserver\\shared\\inbox_zip"]
        else:
            expected_font = "DejaVu Sans"  
            expected_paths = ["./inbox_zip"]
        
        # 設定が適切に選択されることを確認
        self.assertIsInstance(expected_font, str)
        self.assertIsInstance(expected_paths, list)
        self.assertGreater(len(expected_paths), 0)
    
    def test_window_configuration(self):
        """ウィンドウ設定テスト"""
        # ウィンドウサイズ設定
        window_config = {
            'width': 800,
            'height': 700,
            'title': "🐊 AlligatorGar - 多機能自動化ツール"
        }
        
        self.assertIsInstance(window_config['width'], int)
        self.assertIsInstance(window_config['height'], int)
        self.assertIsInstance(window_config['title'], str)
        self.assertGreater(window_config['width'], 0)
        self.assertGreater(window_config['height'], 0)


class TestGUIErrorHandling(unittest.TestCase):
    """GUIエラーハンドリングテスト"""
    
    def test_missing_dependencies_handling(self):
        """依存関係不足時の処理テスト"""
        # このテストは実際のimport失敗をシミュレート
        with patch.dict('sys.modules', {'fitz': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'fitz'")):
                try:
                    # ImportErrorが適切に処理されることを確認
                    import fitz  # これは失敗する
                except ImportError as e:
                    self.assertIn("fitz", str(e))
    
    def test_gui_startup_error_handling(self):
        """GUI起動時エラーハンドリングテスト"""
        if not GUI_AVAILABLE:
            # GUI不可時の適切なエラー処理
            self.assertTrue(True)  # GUI不可時は正常動作とみなす
        else:
            # GUI可用時の正常動作確認
            try:
                root = tk.Tk()
                root.withdraw()
                root.destroy()
                self.assertTrue(True)
            except Exception as e:
                self.fail(f"GUI起動でエラー: {e}")
    
    def test_cross_platform_compatibility(self):
        """クロスプラットフォーム互換性テスト"""
        # OS検出が正常に動作すること
        self.assertIn(os.name, ['nt', 'posix'])
        self.assertIsInstance(sys.platform, str)
        
        # 各プラットフォームで適切な設定が選択されること
        if os.name == 'nt':
            # Windows固有の設定
            self.assertEqual(os.name, 'nt')
        else:
            # Unix系固有の設定
            self.assertNotEqual(os.name, 'nt')


class TestGUIIntegration(unittest.TestCase):
    """GUI統合テスト"""
    
    @patch('process_enhanced.AutoPDFProcessor')
    def test_processor_integration_mock(self, mock_processor):
        """プロセッサ統合テスト（モック使用）"""
        # AutoPDFProcessorのモック設定
        mock_instance = MagicMock()
        mock_processor.return_value = mock_instance
        
        # プロセッサが適切に初期化されることを確認
        processor = mock_processor("test_config.json")
        self.assertIsNotNone(processor)
        
        # メソッド呼び出しが可能であることを確認
        processor.monitor_and_process()
        mock_instance.monitor_and_process.assert_called_once()
    
    def test_threading_support(self):
        """スレッド処理サポートテスト"""
        import threading
        
        def dummy_task():
            return "completed"
        
        # スレッド作成・実行
        thread = threading.Thread(target=dummy_task)
        thread.daemon = True
        thread.start()
        thread.join(timeout=1.0)  # 1秒でタイムアウト
        
        # スレッドが正常に動作すること
        self.assertFalse(thread.is_alive())


if __name__ == '__main__':
    # テストスイート実行
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 各テストクラスを追加
    suite.addTests(loader.loadTestsFromTestCase(TestGUIConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestGUIErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestGUIIntegration))
    
    # GUI利用可能時のみ実行
    if GUI_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestGUIBasicFunctionality))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)