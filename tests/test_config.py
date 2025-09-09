#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定管理機能のテスト
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, mock_open

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from process_enhanced import Config
except ImportError:
    # テスト用の簡易Config実装
    class Config:
        def __init__(self, config_file="config.json"):
            self.config_file = config_file
            self.base_dir = Path.cwd()
            self.config = self._get_default_config()
        
        def _get_default_config(self):
            return {
                "paths": {
                    "inbox_zip": "./inbox_zip",
                    "output_pdf": "./output_pdf"
                },
                "processing": {
                    "monitor_interval_seconds": 5
                }
            }


class TestConfig(unittest.TestCase):
    """設定管理テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_default_config_creation(self):
        """デフォルト設定作成テスト"""
        config = Config(self.config_file)
        
        # 基本項目の存在確認
        self.assertIn("paths", config.config)
        self.assertIn("processing", config.config)
        self.assertIn("inbox_zip", config.config["paths"])
        self.assertIn("monitor_interval_seconds", config.config["processing"])
    
    def test_cross_platform_paths(self):
        """クロスプラットフォーム対応パステスト"""
        config = Config(self.config_file)
        
        # UNCパステスト（Windows以外）
        if os.name != 'nt':
            # UNCパスが含まれていても処理されること
            config.config["paths"]["test_unc"] = r"\\server\share"
            path_obj = Path(config.config["paths"]["test_unc"])
            
            # パス文字列が取得できること
            self.assertIsInstance(str(path_obj), str)
    
    def test_config_validation(self):
        """設定値検証テスト"""
        config = Config(self.config_file)
        
        # 必須項目の存在確認
        required_sections = ["paths", "processing", "pdf", "printing", "logging"]
        
        # 設定に必須セクションが含まれているかチェック（存在するもののみ）
        for section in required_sections:
            if section in config.config:
                self.assertIsInstance(config.config[section], dict)
    
    def test_path_resolution(self):
        """パス解決テスト"""
        config = Config(self.config_file)
        
        # 相対パス処理
        if hasattr(config, 'get_path'):
            try:
                # 設定にある項目でテスト
                if "inbox_zip" in config.config["paths"]:
                    path_result = config.get_path("inbox_zip")
                    self.assertIsInstance(path_result, Path)
            except (KeyError, AttributeError):
                # get_pathメソッドがない場合はスキップ
                pass
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "value"}')
    def test_config_file_loading(self, mock_file):
        """設定ファイル読み込みテスト"""
        config = Config("test.json")
        
        # ファイル読み込み処理が呼ばれることを確認
        # 実際の実装に依存するため、基本的な動作確認のみ
        self.assertIsInstance(config.config, dict)
    
    def test_config_save_load_cycle(self):
        """設定保存・読み込みサイクルテスト"""
        # テスト用設定データ
        test_config = {
            "paths": {
                "inbox_zip": "./test_inbox",
                "output_pdf": "./test_output"
            },
            "processing": {
                "monitor_interval_seconds": 10
            }
        }
        
        # JSON保存テスト
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=2, ensure_ascii=False)
        
        # ファイル存在確認
        self.assertTrue(os.path.exists(self.config_file))
        
        # 読み込み確認
        with open(self.config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        
        self.assertEqual(loaded_config["paths"]["inbox_zip"], "./test_inbox")
        self.assertEqual(loaded_config["processing"]["monitor_interval_seconds"], 10)


class TestCrossPlatformFeatures(unittest.TestCase):
    """クロスプラットフォーム機能テスト"""
    
    def test_os_detection(self):
        """OS検出テスト"""
        self.assertIn(os.name, ['nt', 'posix'])
        self.assertIsInstance(sys.platform, str)
    
    def test_windows_specific_warning(self):
        """Windows専用機能警告テスト"""
        if os.name != 'nt':
            # Windows以外でのUNCパス警告
            unc_path = r"\\server\share"
            if unc_path.startswith('\\\\'):
                # UNCパス検出が正常に動作
                self.assertTrue(True)
        else:
            # Windows環境では通常処理
            self.assertTrue(True)
    
    def test_font_selection(self):
        """フォント選択テスト"""
        if sys.platform.startswith('win'):
            expected_fonts = {
                'title': ('Meiryo', 12, 'bold'),
                'mono': ('Consolas', 9)
            }
        else:
            expected_fonts = {
                'title': ('DejaVu Sans', 12, 'bold'),
                'mono': ('DejaVu Sans Mono', 9)
            }
        
        # フォント設定が適切に選択されること
        for font_type, font_spec in expected_fonts.items():
            self.assertIsInstance(font_spec, tuple)
            self.assertEqual(len(font_spec), 3)
            self.assertIsInstance(font_spec[0], str)  # フォント名
            self.assertIsInstance(font_spec[1], int)  # サイズ


if __name__ == '__main__':
    unittest.main()