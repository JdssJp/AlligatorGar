# 🔰 Python初心者向けガイド

**PDF処理システム開発入門**

## 🎯 このガイドの目的

Python初心者が安全に開発できるように、標準的な開発環境とワークフローを説明します。

## 📋 前提条件

- Ubuntu環境（WSL2でもOK）
- Git基本操作の理解
- テキストエディタ（VS Code推奨）
- GitHubアカウント

## 🚀 クイックスタート（5分で開始）

### ステップ1: リポジトリクローン
```bash
git clone https://github.com/your-username/pdf-processor.git
cd pdf-processor
```

### ステップ2: 環境セットアップ
```bash
# 自動セットアップ実行
./setup-ubuntu.sh

# 仮想環境アクティベート
source venv/bin/activate
```

### ステップ3: 動作確認
```bash
# 基本テスト実行
make test-fast
```

### ステップ4: GUI版実行
```bash
# グラフィカル版を起動
python gui_main.py
```

**これで開発環境完成！** 🎉

## 🔧 開発環境の詳細解説

### 仮想環境とは？

**仮想環境**は、プロジェクト専用のPython環境です。

```bash
# 仮想環境作成（最初の1回だけ）
python3 -m venv venv

# 仮想環境アクティベート（開発時に毎回）
source venv/bin/activate

# 仮想環境から出る
deactivate
```

**なぜ仮想環境を使うの？**
- システムPythonを汚染しない
- プロジェクトごとに異なるライブラリバージョン使用可能
- 環境の再現が簡単

### requirements.txt

プロジェクトに必要なライブラリを記載：

```
PyMuPDF==1.21.1    # PDF処理
Pillow==8.4.0       # 画像処理
reportlab==3.6.0    # PDF生成
pyinstaller==5.13.2 # exe生成
```

```bash
# ライブラリ一括インストール
pip install -r requirements.txt

# インストール済み確認
pip list
```

## 📝 基本的な開発ワークフロー

### 1. 毎回の開発開始時

```bash
# プロジェクトディレクトリに移動
cd pdf-processor

# 仮想環境アクティベート
source venv/bin/activate

# 最新状態に更新
git pull
```

### 2. コード編集

推奨エディタ：**VS Code**
```bash
# VS Codeでプロジェクト開く
code .
```

**初心者向けのファイル**：
- `tests/` - 統合テスト環境
- `gui_main.py` - GUI版メイン
- `requirements.txt` - ライブラリ管理

### 3. テスト実行

```bash
# 基本動作確認
make test-fast

# GUI版起動
python gui_main.py

# Console版起動
python process_enhanced.py
```

### 4. 変更保存（Git）

```bash
# 変更状況確認
git status

# 変更をステージング
git add .

# コミット（変更内容を記録）
git commit -m "機能追加: GUI改善"

# GitHub にアップロード
git push
```

**GitHub に push すると自動的に Windows exe が生成されます！**

## 🛠️ よくあるトラブルと解決法

### ❓ "command not found: python"
```bash
# python3を使用
make test-fast

# または、エイリアス設定
alias python=python3
```

### ❓ "ModuleNotFoundError: No module named..."
```bash
# 仮想環境がアクティベートされているか確認
source venv/bin/activate

# ライブラリ再インストール
pip install -r requirements.txt
```

### ❓ "Permission denied"
```bash
# スクリプト実行権限追加
chmod +x setup-ubuntu.sh
```

### ❓ GUI版が起動しない
```bash
# X11転送確認（WSL2の場合）
echo $DISPLAY

# 必要な場合：
export DISPLAY=:0
```

## 📚 Python基本知識

### ファイル構成の理解

```python
# gui_main.py の基本構造
import tkinter as tk        # GUI作成
import fitz                # PDF処理  
from PIL import Image      # 画像処理

class PDFProcessorGUI:     # メインクラス
    def __init__(self):    # 初期化
        # GUI作成
        
    def start_processing(self):  # 処理開始
        # 実際の処理
        
if __name__ == "__main__":     # プログラム開始点
    app = PDFProcessorGUI()
    app.run()
```

### 設定ファイル（JSON）

```json
{
  "paths": {
    "inbox_zip": "\\\\server\\shared\\inbox",
    "output_pdf": "\\\\server\\shared\\output"
  },
  "processing": {
    "monitor_interval_seconds": 60
  }
}
```

### ログの重要性

```python
# ログ出力例
logger.info("処理開始")           # 情報
logger.warning("警告メッセージ")   # 警告  
logger.error("エラー発生")        # エラー
```

## 🎯 学習ステップ

### レベル1: 基本操作
- [ ] 環境セットアップ完了
- [ ] `make test-fast` 実行成功
- [ ] GUI版起動成功
- [ ] Git基本操作（add, commit, push）

### レベル2: カスタマイズ
- [ ] GUI画面の文字変更
- [ ] 設定値の調整
- [ ] ログメッセージの追加
- [ ] 簡単な機能追加

### レベル3: 機能拡張
- [ ] 新しいタブ追加
- [ ] 処理ロジック改善  
- [ ] エラーハンドリング強化
- [ ] テストケース追加

## 🔗 参考リンク

### 公式ドキュメント
- [Python公式チュートリアル](https://docs.python.org/ja/3/tutorial/)
- [tkinter ドキュメント](https://docs.python.org/ja/3/library/tkinter.html)

### 開発ツール
- [VS Code](https://code.visualstudio.com/)
- [Git入門](https://git-scm.com/book/ja/v2)

### プロジェクト固有
- `project_structure.md` - プロジェクト構成
- `README.md` - プロジェクト概要

## 💬 サポート

困ったときは：
1. **エラーメッセージを読む** - 多くの場合、解決のヒントが含まれています
2. **ログファイル確認** - `*.log` ファイルに詳細情報
3. **Git状態確認** - `git status` で現在の状況を把握
4. **仮想環境確認** - プロンプトに `(venv)` が表示されているか

**🎉 Python開発を楽しみましょう！**