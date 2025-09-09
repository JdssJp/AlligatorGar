#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF処理システム GUI版
Windows用グラフィカルインターフェース
"""

import sys
import os
import json
import threading
import time
from pathlib import Path
from datetime import datetime
import traceback

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    from tkinter import font as tkFont
except ImportError:
    print("tkinter が利用できません。GUI版は動作しません。")
    sys.exit(1)

# PDF処理モジュール
try:
    from process_enhanced import AutoPDFProcessor
except ImportError:
    # 簡易版処理クラス
    class AutoPDFProcessor:
        def __init__(self, config_file="config.json"):
            self.config_file = config_file
            self.running = False
            
        def monitor_and_process(self):
            pass

class PDFProcessorGUI:
    """PDF処理システム GUI メインクラス"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🐊 AlligatorGar - 多機能自動化ツール")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # アプリケーション状態
        self.processor = None
        self.processing_thread = None
        self.is_running = False
        self.config_file = Path("config.json")
        
        # GUI初期化
        self.setup_styles()
        self.create_widgets()
        self.load_config()
        self.center_window()
        
        # 終了処理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """GUI スタイル設定"""
        style = ttk.Style()
        
        # テーマ設定
        try:
            style.theme_use('winnative')  # Windows ネイティブ
        except:
            style.theme_use('default')
        
        # クロスプラットフォーム対応フォント
        if sys.platform.startswith('win'):
            title_font = ('Meiryo', 12, 'bold')
            normal_font = ('Meiryo', 9)
            button_font = ('Meiryo', 10, 'bold')
        else:
            # Linux/Unix用フォント
            title_font = ('DejaVu Sans', 12, 'bold')
            normal_font = ('DejaVu Sans', 9)
            button_font = ('DejaVu Sans', 10, 'bold')
        
        # カスタムスタイル
        style.configure('Title.TLabel', font=title_font)
        style.configure('Status.TLabel', font=normal_font)
        style.configure('Big.TButton', font=button_font, padding=10)
    
    def create_widgets(self):
        """GUI ウィジェット作成"""
        # メニューバー
        self.create_menu()
        
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # タイトル
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, 
                               text="🐊 AlligatorGar", 
                               style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        # アリゲーターガーアイコン
        emoji_font = ('Segoe UI Emoji', 16) if sys.platform.startswith('win') else ('DejaVu Sans', 16)
        icon_label = ttk.Label(title_frame, text="🐊", font=emoji_font)
        icon_label.pack(side=tk.RIGHT)
        
        # ノートブック（タブ）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # タブ作成
        self.create_control_tab()
        self.create_settings_tab()
        self.create_log_tab()
        self.create_about_tab()
    
    def create_menu(self):
        """メニューバー作成"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="設定を開く", command=self.open_config)
        file_menu.add_command(label="設定を保存", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.on_closing)
        
        # 表示メニュー
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="表示", menu=view_menu)
        view_menu.add_command(label="ログクリア", command=self.clear_log)
        view_menu.add_command(label="最新の状態に更新", command=self.refresh_status)
        
        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="使用方法", command=self.show_help)
        help_menu.add_command(label="このアプリについて", command=self.show_about)
    
    def create_control_tab(self):
        """制御タブ作成"""
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text=" 🎮 制御 ")
        
        # 状態表示フレーム
        status_frame = ttk.LabelFrame(control_frame, text="システム状態", padding=10)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 状態ラベル
        self.status_label = ttk.Label(status_frame, 
                                     text="停止中", 
                                     style='Status.TLabel',
                                     foreground='red')
        self.status_label.pack(side=tk.LEFT)
        
        detail_font = ('Meiryo', 8) if sys.platform.startswith('win') else ('DejaVu Sans', 8)
        self.status_detail = ttk.Label(status_frame, 
                                      text="監視を開始してください",
                                      font=detail_font)
        self.status_detail.pack(side=tk.RIGHT)
        
        # 制御ボタンフレーム  
        button_frame = ttk.LabelFrame(control_frame, text="操作", padding=10)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 開始/停止ボタン
        self.start_button = ttk.Button(button_frame,
                                      text="🚀 監視開始",
                                      style='Big.TButton',
                                      command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame,
                                     text="⏹️ 監視停止", 
                                     style='Big.TButton',
                                     command=self.stop_processing,
                                     state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # テストボタン
        self.test_button = ttk.Button(button_frame,
                                     text="🧪 接続テスト",
                                     command=self.test_connection)
        self.test_button.pack(side=tk.RIGHT, padx=5)
        
        # 統計情報フレーム
        stats_frame = ttk.LabelFrame(control_frame, text="処理統計", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 統計表示
        mono_font = ('Consolas', 9) if sys.platform.startswith('win') else ('DejaVu Sans Mono', 9)
        self.stats_text = tk.Text(stats_frame, height=10, wrap=tk.WORD, 
                                 font=mono_font)
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, 
                                       command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初期統計表示
        self.update_stats()
    
    def create_settings_tab(self):
        """設定タブ作成"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text=" ⚙️ 設定 ")
        
        # スクロール可能フレーム
        canvas = tk.Canvas(settings_frame)
        scrollbar = ttk.Scrollbar(settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # パス設定
        path_frame = ttk.LabelFrame(scrollable_frame, text="フォルダパス設定", padding=10)
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 入力ZIP フォルダ
        ttk.Label(path_frame, text="📥 監視フォルダ (ZIP):").pack(anchor=tk.W)
        self.inbox_var = tk.StringVar(value=r"\\fileserver\shared\inbox_zip")
        inbox_frame = ttk.Frame(path_frame)
        inbox_frame.pack(fill=tk.X, pady=2)
        
        self.inbox_entry = ttk.Entry(inbox_frame, textvariable=self.inbox_var, width=60)
        self.inbox_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(inbox_frame, text="📁", width=3, 
                  command=lambda: self.browse_folder(self.inbox_var)).pack(side=tk.RIGHT, padx=(5,0))
        
        # 出力PDF フォルダ
        ttk.Label(path_frame, text="📤 出力フォルダ (PDF):").pack(anchor=tk.W, pady=(10,0))
        self.output_var = tk.StringVar(value=r"\\fileserver\shared\output_pdf") 
        output_frame = ttk.Frame(path_frame)
        output_frame.pack(fill=tk.X, pady=2)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=60)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(output_frame, text="📁", width=3,
                  command=lambda: self.browse_folder(self.output_var)).pack(side=tk.RIGHT, padx=(5,0))
        
        # 処理設定
        process_frame = ttk.LabelFrame(scrollable_frame, text="処理設定", padding=10)
        process_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 監視間隔
        ttk.Label(process_frame, text="⏱️ 監視間隔 (秒):").pack(anchor=tk.W)
        self.interval_var = tk.IntVar(value=60)
        interval_frame = ttk.Frame(process_frame)
        interval_frame.pack(fill=tk.X, pady=2)
        
        ttk.Scale(interval_frame, from_=10, to=300, 
                 orient=tk.HORIZONTAL, variable=self.interval_var,
                 length=200).pack(side=tk.LEFT)
        ttk.Label(interval_frame, textvariable=self.interval_var).pack(side=tk.LEFT, padx=(10,0))
        ttk.Label(interval_frame, text="秒").pack(side=tk.LEFT)
        
        # ファイル保持日数
        ttk.Label(process_frame, text="🗑️ 中間ファイル削除日数:").pack(anchor=tk.W, pady=(10,0))
        self.cleanup_var = tk.IntVar(value=7)
        cleanup_frame = ttk.Frame(process_frame)
        cleanup_frame.pack(fill=tk.X, pady=2)
        
        ttk.Scale(cleanup_frame, from_=1, to=30,
                 orient=tk.HORIZONTAL, variable=self.cleanup_var,
                 length=200).pack(side=tk.LEFT)
        ttk.Label(cleanup_frame, textvariable=self.cleanup_var).pack(side=tk.LEFT, padx=(10,0))
        ttk.Label(cleanup_frame, text="日").pack(side=tk.LEFT)
        
        # 印刷設定
        print_frame = ttk.LabelFrame(scrollable_frame, text="印刷設定", padding=10)
        print_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.auto_print_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(print_frame, text="🖨️ 自動印刷を有効にする",
                       variable=self.auto_print_var).pack(anchor=tk.W)
        
        # 設定ボタン
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(button_frame, text="💾 設定保存", 
                  command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 設定リロード",
                  command=self.load_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔧 デフォルト設定",
                  command=self.reset_config).pack(side=tk.RIGHT, padx=5)
        
        # スクロール設定
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_log_tab(self):
        """ログタブ作成"""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text=" 📋 ログ ")
        
        # ログ制御フレーム
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(log_control_frame, text="システムログ").pack(side=tk.LEFT)
        
        ttk.Button(log_control_frame, text="🔄 更新", 
                  command=self.refresh_log).pack(side=tk.RIGHT, padx=5)
        ttk.Button(log_control_frame, text="🗑️ クリア",
                  command=self.clear_log).pack(side=tk.RIGHT, padx=5)
        ttk.Button(log_control_frame, text="💾 保存",
                  command=self.save_log).pack(side=tk.RIGHT, padx=5)
        
        # ログ表示エリア
        mono_font = ('Consolas', 9) if sys.platform.startswith('win') else ('DejaVu Sans Mono', 9)
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            font=mono_font,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 自動更新チェック
        auto_frame = ttk.Frame(log_frame)
        auto_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_frame, text="自動スクロール",
                       variable=self.auto_scroll_var).pack(side=tk.LEFT)
        
        self.auto_refresh_var = tk.BooleanVar(value=True) 
        ttk.Checkbutton(auto_frame, text="自動更新",
                       variable=self.auto_refresh_var).pack(side=tk.LEFT, padx=10)
    
    def create_about_tab(self):
        """情報タブ作成"""
        about_frame = ttk.Frame(self.notebook)
        self.notebook.add(about_frame, text=" ℹ️ 情報 ")
        
        # アプリ情報
        info_text = f"""
🐊 AlligatorGar - 強力な多機能自動化ツール
═══════════════════════════════════════

バージョン: 2.0.0 (GUI版)
作成日: {datetime.now().strftime('%Y年%m月%d日')}

🎯 現在の主な機能:
• ZIP ファイル自動監視
• PDF スタンプ追加（日付入り「済」印）
• B5 2面付けレイアウト変換  
• 自動印刷・保存
• リアルタイム処理状況表示

🚀 将来の機能拡張:
• 様々な便利機能を追加予定
• 効率的な業務自動化
• カスタマイズ可能なワークフロー

💻 動作環境:
• Windows 10/11
• ネットワーク共有フォルダ対応
• 管理者権限不要

🔧 技術仕様:
• Python {sys.version.split()[0]}
• tkinter GUI
• PyMuPDF (PDF処理)
• PIL/Pillow (画像処理)

📞 サポート:
システムに問題がある場合は、ログタブの内容を
システム管理者にお送りください。

🎨 スタンプデザイン:
上部: 「済」
下部: 「学徒課」  
中央: 処理日付（自動挿入）

© 2024 学徒課システム開発チーム
        """
        
        info_font = ('Meiryo', 9) if sys.platform.startswith('win') else ('DejaVu Sans', 9)
        info_label = ttk.Label(about_frame, text=info_text, 
                              justify=tk.LEFT, font=info_font)
        info_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def center_window(self):
        """ウィンドウを画面中央に配置"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{pos_x}+{pos_y}')
    
    def browse_folder(self, var):
        """フォルダ選択ダイアログ"""
        folder = filedialog.askdirectory(title="フォルダを選択")
        if folder:
            var.set(folder)
    
    def load_config(self):
        """設定読み込み"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # GUI要素に設定値を反映
                self.inbox_var.set(config.get("paths", {}).get("inbox_zip", ""))
                self.output_var.set(config.get("paths", {}).get("output_pdf", ""))
                self.interval_var.set(config.get("processing", {}).get("monitor_interval_seconds", 60))
                self.cleanup_var.set(config.get("processing", {}).get("delete_after_days", 7))
                self.auto_print_var.set(config.get("printing", {}).get("auto_print", True))
                
                self.add_log("設定ファイルを読み込みました")
            else:
                self.add_log("設定ファイルが見つかりません。デフォルト設定を使用します")
        except Exception as e:
            self.add_log(f"設定読み込みエラー: {e}")
            messagebox.showerror("エラー", f"設定の読み込みに失敗しました:\n{e}")
    
    def save_config(self):
        """設定保存"""
        try:
            config = {
                "paths": {
                    "inbox_zip": self.inbox_var.get(),
                    "output_pdf": self.output_var.get(),
                    "local_processed": "processed",
                    "local_unzipped": "unzipped", 
                    "local_stamped": "stamped",
                    "local_print_b5": "print_b5",
                    "stamp_file": "stamp.png"
                },
                "processing": {
                    "monitor_interval_seconds": self.interval_var.get(),
                    "delete_after_days": self.cleanup_var.get(),
                    "max_retries": 3,
                    "retry_delay_seconds": 5
                },
                "pdf_settings": {
                    "stamp_margin": 10,
                    "b5_page_width": 595,
                    "b5_page_height": 842,
                    "enable_date_stamp": True,
                    "font_name": "msgothic.ttc" if sys.platform.startswith('win') else "DejaVu Sans",
                    "font_size": 18
                },
                "logging": {
                    "level": "INFO",
                    "max_file_size_mb": 10,
                    "backup_count": 5,
                    "log_file": "autopdf.log"
                },
                "printing": {
                    "auto_print": self.auto_print_var.get(),
                    "print_timeout_seconds": 60
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.add_log("設定ファイルを保存しました")
            messagebox.showinfo("保存完了", "設定を保存しました")
            
        except Exception as e:
            self.add_log(f"設定保存エラー: {e}")
            messagebox.showerror("エラー", f"設定の保存に失敗しました:\n{e}")
    
    def reset_config(self):
        """設定リセット"""
        if messagebox.askyesno("確認", "設定をデフォルトにリセットしますか？"):
            self.inbox_var.set(r"\\fileserver\shared\inbox_zip")
            self.output_var.set(r"\\fileserver\shared\output_pdf")
            self.interval_var.set(60)
            self.cleanup_var.set(7)
            self.auto_print_var.set(True)
            self.add_log("設定をデフォルトにリセットしました")
    
    def start_processing(self):
        """処理開始"""
        if self.is_running:
            return
        
        try:
            # 設定保存
            self.save_config()
            
            # プロセッサ初期化
            self.processor = AutoPDFProcessor(str(self.config_file))
            
            # 処理スレッド開始
            self.processing_thread = threading.Thread(
                target=self.run_processor, 
                daemon=True
            )
            self.processing_thread.start()
            
            # UI状態更新
            self.is_running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.update_status("実行中", "監視処理中...", 'green')
            
            self.add_log("PDF処理監視を開始しました")
            
        except Exception as e:
            self.add_log(f"開始エラー: {e}")
            messagebox.showerror("エラー", f"処理の開始に失敗しました:\n{e}")
    
    def stop_processing(self):
        """処理停止"""
        if not self.is_running:
            return
        
        try:
            self.is_running = False
            
            # UI状態更新
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.update_status("停止中", "処理を停止しました", 'red')
            
            self.add_log("PDF処理監視を停止しました")
            
        except Exception as e:
            self.add_log(f"停止エラー: {e}")
            messagebox.showerror("エラー", f"処理の停止に失敗しました:\n{e}")
    
    def run_processor(self):
        """プロセッサ実行（別スレッド）"""
        try:
            while self.is_running:
                # ここで実際の処理を行う
                time.sleep(self.interval_var.get())
                
                if self.auto_refresh_var.get():
                    self.root.after(0, self.refresh_log)
                    self.root.after(0, self.update_stats)
                
        except Exception as e:
            self.root.after(0, lambda: self.add_log(f"処理エラー: {e}"))
    
    def test_connection(self):
        """接続テスト"""
        def test_thread():
            try:
                self.add_log("接続テストを開始...")
                
                # フォルダ存在確認
                inbox_path = Path(self.inbox_var.get())
                output_path = Path(self.output_var.get())
                
                inbox_ok = inbox_path.exists()
                output_ok = output_path.exists() or output_path.parent.exists()
                
                self.add_log(f"監視フォルダ: {inbox_path} {'✓' if inbox_ok else '✗'}")
                self.add_log(f"出力フォルダ: {output_path} {'✓' if output_ok else '✗'}")
                
                if inbox_ok and output_ok:
                    self.add_log("接続テスト: 成功 ✓")
                    self.root.after(0, lambda: messagebox.showinfo("テスト結果", "接続テストが成功しました！"))
                else:
                    self.add_log("接続テスト: 失敗 ✗")
                    self.root.after(0, lambda: messagebox.showwarning("テスト結果", "一部のフォルダに接続できません"))
                    
            except Exception as e:
                self.add_log(f"接続テストエラー: {e}")
                self.root.after(0, lambda: messagebox.showerror("エラー", f"接続テストでエラーが発生しました:\n{e}"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def update_status(self, status, detail, color='black'):
        """ステータス更新"""
        self.status_label.config(text=status, foreground=color)
        self.status_detail.config(text=detail)
    
    def update_stats(self):
        """統計情報更新"""
        try:
            stats_info = f"""処理統計情報
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 基本情報:
　システム状態: {'実行中' if self.is_running else '停止中'}
　最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
　監視間隔: {self.interval_var.get()}秒

📁 設定パス:
　監視フォルダ: {self.inbox_var.get()}
　出力フォルダ: {self.output_var.get()}

🎯 処理設定:
　自動印刷: {'有効' if self.auto_print_var.get() else '無効'}
　ファイル保持: {self.cleanup_var.get()}日間

💻 システム情報:
　Python: {sys.version.split()[0]}
　作業ディレクトリ: {os.getcwd()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert('1.0', stats_info)
            
        except Exception as e:
            self.add_log(f"統計更新エラー: {e}")
    
    def add_log(self, message):
        """ログ追加"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.config(state=tk.DISABLED)
        
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
    
    def clear_log(self):
        """ログクリア"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.add_log("ログをクリアしました")
    
    def refresh_log(self):
        """ログ更新"""
        # 実際のログファイルから読み込み処理をここに追加
        self.add_log("ログを更新しました")
    
    def save_log(self):
        """ログ保存"""
        try:
            filename = filedialog.asksaveasfilename(
                title="ログファイルを保存",
                defaultextension=".txt",
                filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get('1.0', tk.END))
                
                self.add_log(f"ログを保存しました: {filename}")
                messagebox.showinfo("保存完了", "ログファイルを保存しました")
                
        except Exception as e:
            self.add_log(f"ログ保存エラー: {e}")
            messagebox.showerror("エラー", f"ログの保存に失敗しました:\n{e}")
    
    def refresh_status(self):
        """状態更新"""
        self.update_stats()
        self.add_log("状態を更新しました")
    
    def open_config(self):
        """設定ファイルを開く"""
        try:
            os.startfile(str(self.config_file))
        except Exception as e:
            messagebox.showerror("エラー", f"設定ファイルを開けませんでした:\n{e}")
    
    def show_help(self):
        """ヘルプ表示"""
        help_text = """
PDF処理自動化システム - 使用方法

1. 設定タブで監視フォルダと出力フォルダを設定
2. 制御タブで「監視開始」ボタンを押す
3. ZIPファイルが監視フォルダに追加されると自動処理開始
4. 処理結果は出力フォルダに保存される
5. ログタブで処理状況を確認

※ ネットワークフォルダを指定する場合は
   \\\\server\\share 形式で入力してください
        """
        messagebox.showinfo("使用方法", help_text)
    
    def show_about(self):
        """アプリについて"""
        about_text = f"""
PDF処理自動化システム v2.0.0

学徒課向け文書処理自動化ツール

開発: システム開発チーム
作成日: {datetime.now().strftime('%Y年%m月%d日')}

このソフトウェアは内部使用目的で作成されています。
        """
        messagebox.showinfo("このアプリについて", about_text)
    
    def on_closing(self):
        """アプリ終了処理"""
        if self.is_running:
            if messagebox.askokcancel("確認", "処理が実行中です。終了しますか？"):
                self.stop_processing()
                time.sleep(1)  # 停止処理待機
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """GUI実行"""
        try:
            self.add_log("PDF処理システムを開始しました")
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("致命的エラー", f"アプリケーション実行エラー:\n{e}")
            traceback.print_exc()

def main():
    """メイン関数"""
    try:
        app = PDFProcessorGUI()
        app.run()
    except Exception as e:
        print(f"GUI起動エラー: {e}")
        traceback.print_exc()
        input("エラーが発生しました。何かキーを押してください...")

if __name__ == "__main__":
    main()