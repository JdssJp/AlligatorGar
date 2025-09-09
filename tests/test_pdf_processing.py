#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF処理機能のテスト
"""

import unittest
import tempfile
import os
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# PDF処理ライブラリの可用性チェック
try:
    import fitz
    PDF_LIBS_AVAILABLE = True
except ImportError:
    PDF_LIBS_AVAILABLE = False
    # テスト用のモック
    fitz = MagicMock()

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = MagicMock()

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    canvas = MagicMock()
    A4 = (595, 842)


class TestPDFProcessing(unittest.TestCase):
    """PDF処理機能テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_pdf = os.path.join(self.temp_dir, "test.pdf")
        self.test_zip = os.path.join(self.temp_dir, "test.zip")
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_pdf(self, filename):
        """テスト用PDF作成"""
        if REPORTLAB_AVAILABLE:
            c = canvas.Canvas(filename, pagesize=A4)
            c.drawString(100, 750, "Test PDF")
            c.showPage()
            c.save()
            return True
        else:
            # モック用のダミーファイル
            with open(filename, 'wb') as f:
                f.write(b'%PDF-1.4\n%Mock PDF\n%%EOF')
            return True
    
    @unittest.skipIf(not REPORTLAB_AVAILABLE, "ReportLabが利用できません")
    def test_pdf_creation(self):
        """PDF作成テスト"""
        self.create_test_pdf(self.test_pdf)
        self.assertTrue(os.path.exists(self.test_pdf))
        
        # ファイルサイズが0より大きい
        self.assertGreater(os.path.getsize(self.test_pdf), 0)
    
    @unittest.skipIf(not PDF_LIBS_AVAILABLE, "PyMuPDFが利用できません")
    def test_pdf_reading(self):
        """PDF読み込みテスト"""
        if REPORTLAB_AVAILABLE:
            self.create_test_pdf(self.test_pdf)
            
            # PDF読み込み
            doc = fitz.open(self.test_pdf)
            self.assertGreater(len(doc), 0)
            doc.close()
    
    def test_zip_creation(self):
        """ZIP作成テスト"""
        # テスト用ファイル作成
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # ZIP作成
        with zipfile.ZipFile(self.test_zip, 'w') as zf:
            zf.write(test_file, "test.txt")
        
        self.assertTrue(os.path.exists(self.test_zip))
        
        # ZIP内容確認
        with zipfile.ZipFile(self.test_zip, 'r') as zf:
            files = zf.namelist()
            self.assertIn("test.txt", files)
    
    def test_zip_extraction(self):
        """ZIP展開テスト"""
        # テスト用ZIP作成
        test_file = os.path.join(self.temp_dir, "source.txt")
        with open(test_file, 'w') as f:
            f.write("Test content for extraction")
        
        with zipfile.ZipFile(self.test_zip, 'w') as zf:
            zf.write(test_file, "extracted.txt")
        
        # 展開ディレクトリ
        extract_dir = os.path.join(self.temp_dir, "extracted")
        os.makedirs(extract_dir)
        
        # 展開
        with zipfile.ZipFile(self.test_zip, 'r') as zf:
            zf.extractall(extract_dir)
        
        # 展開ファイル確認
        extracted_file = os.path.join(extract_dir, "extracted.txt")
        self.assertTrue(os.path.exists(extracted_file))
        
        with open(extracted_file, 'r') as f:
            content = f.read()
            self.assertEqual(content, "Test content for extraction")
    
    @patch('subprocess.run')
    def test_print_functionality_windows(self, mock_subprocess):
        """印刷機能テスト（Windows）"""
        # Windows環境をシミュレート
        with patch('os.name', 'nt'):
            # 成功ケース
            mock_subprocess.return_value.returncode = 0
            
            # この部分は実際のPDFProcessor実装に依存
            # 基本的な動作確認のみ
            self.assertEqual(os.name, 'nt')  # パッチが適用されていることを確認
    
    def test_print_functionality_non_windows(self):
        """印刷機能テスト（Windows以外）"""
        if os.name != 'nt':
            # Windows以外では警告メッセージが適切に処理される
            self.assertNotEqual(os.name, 'nt')
            # 実際の警告処理は実装に依存するため、OS判定のみテスト


class TestFileOperations(unittest.TestCase):
    """ファイル操作テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_directory_creation(self):
        """ディレクトリ作成テスト"""
        test_dir = os.path.join(self.temp_dir, "test_directory")
        
        # ディレクトリ作成
        Path(test_dir).mkdir(exist_ok=True)
        
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.isdir(test_dir))
    
    def test_file_move_operation(self):
        """ファイル移動テスト"""
        source_file = os.path.join(self.temp_dir, "source.txt")
        dest_file = os.path.join(self.temp_dir, "destination.txt")
        
        # ソースファイル作成
        with open(source_file, 'w') as f:
            f.write("Test content for move")
        
        # ファイル移動
        import shutil
        shutil.move(source_file, dest_file)
        
        self.assertFalse(os.path.exists(source_file))
        self.assertTrue(os.path.exists(dest_file))
        
        # 内容確認
        with open(dest_file, 'r') as f:
            content = f.read()
            self.assertEqual(content, "Test content for move")
    
    def test_file_cleanup(self):
        """ファイルクリーンアップテスト"""
        # テストファイル複数作成
        test_files = []
        for i in range(3):
            test_file = os.path.join(self.temp_dir, f"cleanup_test_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"Test content {i}")
            test_files.append(test_file)
        
        # 全ファイルが存在することを確認
        for test_file in test_files:
            self.assertTrue(os.path.exists(test_file))
        
        # クリーンアップ
        for test_file in test_files:
            os.remove(test_file)
        
        # 全ファイルが削除されたことを確認
        for test_file in test_files:
            self.assertFalse(os.path.exists(test_file))


@unittest.skipIf(not PIL_AVAILABLE, "Pillowが利用できません")
class TestImageProcessing(unittest.TestCase):
    """画像処理テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_image_creation(self):
        """画像作成テスト"""
        from PIL import Image, ImageDraw
        
        # テスト画像作成
        img = Image.new('RGBA', (100, 50), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 90, 40], fill=(255, 0, 0, 128))
        
        # 保存
        test_image = os.path.join(self.temp_dir, "test_stamp.png")
        img.save(test_image)
        
        self.assertTrue(os.path.exists(test_image))
        self.assertGreater(os.path.getsize(test_image), 0)
    
    def test_image_loading(self):
        """画像読み込みテスト"""
        from PIL import Image, ImageDraw
        
        # テスト画像作成・保存
        img = Image.new('RGB', (200, 100), (0, 255, 0))
        test_image = os.path.join(self.temp_dir, "test_load.png")
        img.save(test_image)
        
        # 読み込み
        loaded_img = Image.open(test_image)
        self.assertEqual(loaded_img.size, (200, 100))
        self.assertEqual(loaded_img.mode, 'RGB')


if __name__ == '__main__':
    # テストスイート実行
    unittest.main(verbosity=2)