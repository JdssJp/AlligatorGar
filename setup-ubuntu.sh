#!/bin/bash
# Ubuntu開発環境セットアップ（Python初心者向け）

echo "📚 PDF処理システム開発環境セットアップ"
echo "========================================"

# Python3確認・インストール
echo "🐍 Python3 インストール確認..."
if ! command -v python3 &> /dev/null; then
    echo "Python3をインストールします..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
else
    echo "✓ Python3 は既にインストール済み"
fi

# 仮想環境作成
echo ""
echo "📦 仮想環境作成..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ 仮想環境 'venv' を作成しました"
else
    echo "✓ 仮想環境は既に存在します"
fi

# 仮想環境アクティベート
echo ""
echo "⚡ 仮想環境をアクティベート..."
source venv/bin/activate

# 必要ライブラリインストール
echo ""
echo "📚 必要なライブラリをインストール..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ セットアップ完了！"
echo ""
echo "🚀 次のステップ:"
echo "1. 仮想環境をアクティベート: source venv/bin/activate"
echo "2. テスト実行: python test_basic.py"
echo "3. GUI版実行: python gui_main.py"
echo "4. 設定確認: python -c 'import fitz, PIL; print(\"OK\")'"
echo ""