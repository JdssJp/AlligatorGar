#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF処理自動化システム (強化版)
Windows 10 32bit対応 - 本格運用版

機能:
- ZIP ファイル監視・自動処理
- PDF スタンプ追加（日付入り）
- B5 2面付けレイアウト
- 自動印刷・ファイル保存
- 包括的ログ・エラーハンドリング
"""

import sys
import os
import zipfile
import shutil
import json
import logging
import logging.handlers
from pathlib import Path
import time
from datetime import datetime, timedelta
import traceback
import subprocess
from typing import List, Optional, Dict, Any

# PDF/画像処理
try:
    import fitz  # PyMuPDF
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import ImageReader
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    print(f"必要なライブラリが不足しています: {e}")
    print("pip install PyMuPDF reportlab Pillow を実行してください")
    sys.exit(1)

# ===== 設定管理 =====
class Config:
    """設定管理クラス"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.base_dir = Path(__file__).parent
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        default_config = {
            "paths": {
                "inbox_zip": r"\\fileserver\shared\inbox_zip",
                "output_pdf": r"\\fileserver\shared\output_pdf",
                "local_processed": "processed",
                "local_unzipped": "unzipped",
                "local_stamped": "stamped",
                "local_print_b5": "print_b5",
                "stamp_file": "stamp.png"
            },
            "processing": {
                "monitor_interval_seconds": 60,
                "delete_after_days": 7,
                "max_retries": 3,
                "retry_delay_seconds": 5
            },
            "pdf_settings": {
                "stamp_margin": 10,
                "b5_page_width": 595,
                "b5_page_height": 842,
                "enable_date_stamp": True,
                "font_name": "msgothic.ttc",
                "font_size": 18
            },
            "logging": {
                "level": "INFO",
                "max_file_size_mb": 10,
                "backup_count": 5,
                "log_file": "autopdf.log"
            },
            "printing": {
                "auto_print": True,
                "print_timeout_seconds": 60
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # デフォルト設定に上書き
                self._deep_update(default_config, user_config)
                return default_config
            except Exception as e:
                print(f"設定ファイル読み込みエラー: {e}")
                print("デフォルト設定を使用します")
        else:
            # デフォルト設定ファイル作成
            self._save_config(default_config)
            
        return default_config
    
    def _deep_update(self, base_dict: dict, update_dict: dict):
        """辞書の深い更新"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _save_config(self, config: dict):
        """設定ファイル保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"設定ファイル保存エラー: {e}")
    
    def get_path(self, key: str) -> Path:
        """パス取得（相対パスは絶対パスに変換）"""
        path_str = self.config["paths"][key]
        path_obj = Path(path_str)
        
        # UNCパスの警告（Windows以外）
        if str(path_obj).startswith('\\\\') and os.name != 'nt':
            import logging
            logger = logging.getLogger("AutoPDF")
            logger.warning(f"UNCパス '{path_str}' はWindows専用です (現在のOS: {os.name})")
            logger.info(f"ローカルパスとして処理を試行します")
        
        # UNCパスや絶対パスはそのまま、相対パスはbase_dir基準
        if path_obj.is_absolute() or str(path_obj).startswith('\\\\'):
            return path_obj
        else:
            return self.base_dir / path_obj

# ===== ログ設定 =====
def setup_logging(config: Config) -> logging.Logger:
    """ログシステム設定"""
    log_config = config.config["logging"]
    
    logger = logging.getLogger("AutoPDF")
    logger.setLevel(getattr(logging, log_config["level"]))
    
    # ファイルハンドラ（ローテーション付き）
    log_file = config.base_dir / log_config["log_file"]
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=log_config["max_file_size_mb"] * 1024 * 1024,
        backupCount=log_config["backup_count"],
        encoding='utf-8'
    )
    
    # コンソールハンドラ
    console_handler = logging.StreamHandler(sys.stdout)
    
    # フォーマット設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# ===== PDF処理クラス =====
class PDFProcessor:
    """PDF処理クラス"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.pdf_settings = config.config["pdf_settings"]
        
    def create_date_stamp(self, base_stamp_path: Path, date_text: str) -> Optional[Path]:
        """日付入りスタンプ作成"""
        try:
            if not base_stamp_path.exists():
                self.logger.error(f"スタンプファイルが見つかりません: {base_stamp_path}")
                return None
                
            base_img = Image.open(base_stamp_path).convert("RGBA")
            txt_img = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(txt_img)
            
            # フォント設定
            try:
                font = ImageFont.truetype(
                    self.pdf_settings["font_name"], 
                    self.pdf_settings["font_size"]
                )
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", self.pdf_settings["font_size"])
                except:
                    font = ImageFont.load_default()
                    self.logger.warning("デフォルトフォントを使用します")
            
            # テキストサイズ取得
            bbox = draw.textbbox((0, 0), date_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 日付をスタンプ中央下に配置
            x = (base_img.width - text_width) // 2
            y = base_img.height // 2
            draw.text((x, y), date_text, fill=(0, 0, 0, 255), font=font)
            
            # 合成
            combined = Image.alpha_composite(base_img, txt_img)
            
            # 一時ファイル保存
            tmp_stamp = self.config.base_dir / f"tmp_stamp_{int(time.time())}.png"
            combined.save(tmp_stamp)
            
            self.logger.debug(f"日付入りスタンプ作成: {tmp_stamp}")
            return tmp_stamp
            
        except Exception as e:
            self.logger.error(f"スタンプ作成エラー: {e}")
            return None
    
    def add_stamp_to_pdf(self, input_pdf: Path, output_pdf: Path, stamp_file: Path) -> bool:
        """PDFにスタンプ追加"""
        try:
            doc = fitz.open(str(input_pdf))
            
            for page in doc:
                rect = page.rect
                
                # スタンプサイズ取得
                stamp_img = Image.open(stamp_file)
                stamp_width, stamp_height = stamp_img.size
                
                # 右下に配置
                margin = self.pdf_settings["stamp_margin"]
                stamp_rect = fitz.Rect(
                    rect.width - stamp_width - margin,
                    rect.height - stamp_height - margin,
                    rect.width - margin,
                    rect.height - margin
                )
                
                page.insert_image(stamp_rect, filename=str(stamp_file))
            
            # 出力ディレクトリ作成
            output_pdf.parent.mkdir(parents=True, exist_ok=True)
            
            doc.save(str(output_pdf))
            doc.close()
            
            self.logger.debug(f"スタンプ追加完了: {output_pdf}")
            return True
            
        except Exception as e:
            self.logger.error(f"スタンプ追加エラー {input_pdf}: {e}")
            return False
    
    def create_b5_2up(self, input_pdfs: List[Path], output_pdf: Path) -> bool:
        """B5 2面付けPDF作成"""
        try:
            doc_out = fitz.open()
            
            for pdf_file in input_pdfs:
                self.logger.debug(f"2面付け処理: {pdf_file}")
                doc_in = fitz.open(str(pdf_file))
                
                for i in range(0, len(doc_in), 2):
                    # B5横2面のページ作成
                    page_width = self.pdf_settings["b5_page_width"] * 2
                    page_height = self.pdf_settings["b5_page_height"]
                    page_out = doc_out.new_page(width=page_width, height=page_height)
                    
                    # 左ページ
                    left_rect = fitz.Rect(0, 0, self.pdf_settings["b5_page_width"], page_height)
                    page_out.show_pdf_page(left_rect, doc_in, i)
                    
                    # 右ページ（存在する場合）
                    if i + 1 < len(doc_in):
                        right_rect = fitz.Rect(
                            self.pdf_settings["b5_page_width"], 0, 
                            page_width, page_height
                        )
                        page_out.show_pdf_page(right_rect, doc_in, i + 1)
                
                doc_in.close()
            
            # 出力ディレクトリ作成
            output_pdf.parent.mkdir(parents=True, exist_ok=True)
            
            doc_out.save(str(output_pdf))
            doc_out.close()
            
            self.logger.info(f"B5 2面付けPDF作成完了: {output_pdf}")
            return True
            
        except Exception as e:
            self.logger.error(f"B5 2面付けエラー: {e}")
            return False

# ===== ファイル処理クラス =====
class FileProcessor:
    """ファイル処理クラス"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.processing_config = config.config["processing"]
        
    def extract_zip(self, zip_path: Path, extract_dir: Path) -> bool:
        """ZIP解凍"""
        try:
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            self.logger.debug(f"ZIP解凍完了: {zip_path} -> {extract_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"ZIP解凍エラー {zip_path}: {e}")
            return False
    
    def extract_date_from_filename(self, filename: str) -> str:
        """ファイル名から日付抽出"""
        try:
            # P_20250908_00720-9-00017455.zip パターン
            parts = filename.split("_")
            if len(parts) >= 2 and len(parts[1]) == 8:
                date_str = parts[1]
                # 日付フォーマット確認
                datetime.strptime(date_str, "%Y%m%d")
                return date_str
        except:
            pass
        
        # デフォルトは今日の日付
        return datetime.now().strftime("%Y%m%d")
    
    def cleanup_old_files(self, folder: Path, days: int = None) -> None:
        """古いファイル削除"""
        try:
            if not folder.exists():
                return
                
            if days is None:
                days = self.processing_config["delete_after_days"]
                
            cutoff = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            for item in folder.glob("*"):
                try:
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    if mtime < cutoff:
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                        deleted_count += 1
                except Exception as e:
                    self.logger.warning(f"ファイル削除エラー {item}: {e}")
            
            if deleted_count > 0:
                self.logger.info(f"{folder}から{deleted_count}個の古いファイルを削除")
                
        except Exception as e:
            self.logger.error(f"クリーンアップエラー {folder}: {e}")
    
    def print_pdf(self, pdf_file: Path) -> bool:
        """PDF印刷"""
        try:
            if not self.config.config["printing"]["auto_print"]:
                self.logger.info("自動印刷は無効化されています")
                return True
            
            # Windows専用機能の確認
            if os.name != 'nt':
                self.logger.warning(f"印刷機能はWindows専用です (現在のOS: {os.name})")
                self.logger.info(f"PDFファイルは保存されました: {pdf_file}")
                return True
                
            timeout = self.config.config["printing"]["print_timeout_seconds"]
            
            # Adobe Reader での印刷
            cmd = ["cmd", "/c", "start", "/min", "/wait", "AcroRd32.exe", "/p", str(pdf_file)]
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                timeout=timeout,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info(f"印刷完了: {pdf_file}")
                return True
            else:
                self.logger.error(f"印刷エラー {pdf_file}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"印刷タイムアウト: {pdf_file}")
            return False
        except Exception as e:
            self.logger.error(f"印刷エラー {pdf_file}: {e}")
            return False

# ===== メインプロセッサ =====
class AutoPDFProcessor:
    """メイン処理クラス"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = Config(config_file)
        self.logger = setup_logging(self.config)
        self.pdf_processor = PDFProcessor(self.config, self.logger)
        self.file_processor = FileProcessor(self.config, self.logger)
        
        self.logger.info("AutoPDF Processor 初期化完了")
        self._create_directories()
    
    def _create_directories(self):
        """必要なディレクトリ作成"""
        directories = [
            "local_processed", "local_unzipped", 
            "local_stamped", "local_print_b5"
        ]
        
        for dir_key in directories:
            try:
                dir_path = self.config.get_path(dir_key)
                dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"ディレクトリ確認: {dir_path}")
            except Exception as e:
                self.logger.error(f"ディレクトリ作成エラー {dir_key}: {e}")
    
    def process_zip_file(self, zip_path: Path) -> bool:
        """単一ZIPファイル処理"""
        self.logger.info(f"処理開始: {zip_path.name}")
        
        try:
            # 1. 日付抽出
            date_text = self.file_processor.extract_date_from_filename(zip_path.stem)
            self.logger.debug(f"抽出した日付: {date_text}")
            
            # 2. スタンプ作成
            stamp_file = self.config.get_path("stamp_file")
            if self.config.config["pdf_settings"]["enable_date_stamp"]:
                tmp_stamp = self.pdf_processor.create_date_stamp(stamp_file, date_text)
                if not tmp_stamp:
                    self.logger.error("スタンプ作成に失敗")
                    return False
            else:
                tmp_stamp = stamp_file
            
            # 3. ZIP解凍
            unzipped_dir = self.config.get_path("local_unzipped")
            if not self.file_processor.extract_zip(zip_path, unzipped_dir):
                return False
            
            # 4. PDF処理
            stamped_files = []
            pdf_files = list(unzipped_dir.glob("*.pdf"))
            
            if not pdf_files:
                self.logger.warning(f"PDFファイルが見つかりません: {zip_path.name}")
                return False
            
            stamped_dir = self.config.get_path("local_stamped")
            
            for pdf_file in pdf_files:
                stamped_file = stamped_dir / pdf_file.name
                if self.pdf_processor.add_stamp_to_pdf(pdf_file, stamped_file, tmp_stamp):
                    stamped_files.append(stamped_file)
                else:
                    self.logger.error(f"スタンプ追加失敗: {pdf_file}")
            
            if not stamped_files:
                self.logger.error("スタンプ処理されたPDFがありません")
                return False
            
            # 5. B5 2面付け
            output_pdf = self.config.get_path("output_pdf") / f"{zip_path.stem}_B5.pdf"
            if not self.pdf_processor.create_b5_2up(stamped_files, output_pdf):
                return False
            
            # 6. 印刷
            self.file_processor.print_pdf(output_pdf)
            
            # 7. ZIP移動
            processed_dir = self.config.get_path("local_processed")
            processed_dir.mkdir(parents=True, exist_ok=True)
            processed_zip = processed_dir / zip_path.name
            shutil.move(str(zip_path), str(processed_zip))
            
            # 8. 一時ファイル削除
            if tmp_stamp != stamp_file and tmp_stamp.exists():
                tmp_stamp.unlink()
            
            self.logger.info(f"処理完了: {zip_path.name} -> {output_pdf.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"処理エラー {zip_path.name}: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def monitor_and_process(self):
        """監視・処理ループ"""
        self.logger.info("ファイル監視開始")
        
        inbox_dir = self.config.get_path("inbox_zip")
        interval = self.config.config["processing"]["monitor_interval_seconds"]
        
        while True:
            try:
                # 新しいZIPファイルをチェック
                if inbox_dir.exists():
                    zip_files = list(inbox_dir.glob("*.zip"))
                    
                    for zip_file in zip_files:
                        # リトライ機構
                        max_retries = self.config.config["processing"]["max_retries"]
                        retry_delay = self.config.config["processing"]["retry_delay_seconds"]
                        
                        success = False
                        for attempt in range(max_retries):
                            if attempt > 0:
                                self.logger.info(f"リトライ {attempt}/{max_retries-1}: {zip_file.name}")
                                time.sleep(retry_delay)
                            
                            if self.process_zip_file(zip_file):
                                success = True
                                break
                        
                        if not success:
                            self.logger.error(f"処理失敗（最大リトライ数到達）: {zip_file.name}")
                
                # 定期クリーンアップ
                self.file_processor.cleanup_old_files(self.config.get_path("local_unzipped"))
                self.file_processor.cleanup_old_files(self.config.get_path("local_stamped"))
                self.file_processor.cleanup_old_files(self.config.get_path("local_print_b5"))
                
                # 待機
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.logger.info("ユーザーによる停止")
                break
            except Exception as e:
                self.logger.error(f"監視ループエラー: {e}")
                self.logger.error(traceback.format_exc())
                time.sleep(interval)

# ===== エントリーポイント =====
def main():
    """メイン関数"""
    print("PDF処理自動化システム (強化版)")
    print("=" * 50)
    
    try:
        # システム情報表示
        print(f"Python版本: {sys.version}")
        print(f"実行ディレクトリ: {Path(__file__).parent}")
        print(f"開始時刻: {datetime.now()}")
        print()
        
        # プロセッサ初期化・実行
        processor = AutoPDFProcessor()
        processor.monitor_and_process()
        
    except Exception as e:
        print(f"システムエラー: {e}")
        traceback.print_exc()
        
        # ログにも記録
        try:
            logger = logging.getLogger("AutoPDF")
            logger.critical(f"システム停止エラー: {e}")
            logger.critical(traceback.format_exc())
        except:
            pass
    
    finally:
        print("システム終了")

if __name__ == "__main__":
    main()