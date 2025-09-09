# 🐊 AlligatorGar（初心者向け）

**Python初心者でも安心！** 強力な多機能自動化ツール - 標準的な開発環境で Windows exe を自動生成

## 🚀 5分でスタート

### Ubuntu開発環境
```bash
# 1. リポジトリクローン
git clone https://github.com/jdssjp/AlligatorGar.git
cd AlligatorGar

# 2. 開発環境セットアップ
make setup

# 3. 仮想環境アクティベート  
source venv/bin/activate

# 4. テスト実行
make test-fast

# 5. GUI版起動
make run-gui
```

### Windows実行ファイル取得
1. **GitHub** → **Releases** → **最新リリース**
2. **Assets** から実行ファイルをダウンロード
3. ダブルクリックで即実行！

## 📁 シンプルなファイル構成

```
AlligatorGar/
├── 🐍 メインプログラム
│   ├── gui_main.py              # GUI版（初心者推奨）
│   └── process_enhanced.py      # Console版
│
├── 🧪 テストスイート
│   └── tests/                   # 統合テスト環境
│       ├── test_config.py       # 設定機能テスト
│       ├── test_gui.py          # GUI機能テスト
│       └── test_pdf_processing.py # PDF処理テスト
│
├── 🛠️ 開発環境
│   ├── requirements.txt         # 本番依存関係
│   ├── requirements-dev.txt     # 開発依存関係
│   ├── pyproject.toml          # モダンPython設定
│   ├── Makefile                # 開発タスクランナー
│   └── setup-ubuntu.sh         # Ubuntu自動セットアップ
│
├── 🚀 GitHub CI/CD
│   └── .github/
│       ├── workflows/
│       │   ├── ci.yml          # テスト自動実行
│       │   └── build-simple.yml # Windows exe自動生成
│       └── dependabot.yml       # 依存関係自動更新
│
└── 📚 ドキュメント
    ├── README.md               # このファイル
    ├── DEVELOPMENT.md          # 開発者向けガイド
    └── BEGINNER_GUIDE.md       # 初心者向けガイド
```

## 🎯 2つのバージョン

### 🖥️ GUI版（初心者推奨）
- **ファイル**: `AlligatorGar_GUI.exe`
- **特徴**: わかりやすい画面操作、リアルタイム表示
- **使用方法**: ダブルクリック → 設定 → 監視開始

### 🖤 Console版（上級者・サーバー用）  
- **ファイル**: `AlligatorGar_Console.exe`
- **特徴**: 軽量、JSON設定、ログ出力
- **使用方法**: ダブルクリック → config.json編集 → 再実行

## 🔧 開発環境（Ubuntu）

### 標準的なPython開発
```bash
# 仮想環境作成（標準的な方法）
python3 -m venv venv

# 仮想環境アクティベート
source venv/bin/activate

# ライブラリインストール  
pip install -r requirements.txt
```

### 必要ライブラリ（シンプル構成）
```
PyMuPDF==1.21.1    # PDF処理
Pillow==8.4.0       # 画像処理  
reportlab==3.6.0    # PDF生成
pyinstaller==5.13.2 # exe生成
```

### 開発ツール（自動インストール）
```
pytest              # テストフレームワーク
coverage            # テストカバレッジ
black               # コードフォーマット
flake8              # コード品質チェック
```

## 🚀 GitHub自動ビルド

### 仕組み
1. **Ubuntu で開発** → Python コード編集
2. **GitHub リリース作成** → 自動的に Windows exe 生成  
3. **Windows で使用** → リリースページからダウンロードして即実行

### 自動生成される成果物
- `AlligatorGar_GUI.exe` - GUI版実行ファイル
- `AlligatorGar_Console.exe` - Console版実行ファイル
- 配布用パッケージ（README付き）

## 📚 初心者向けサポート

### 学習ステップ
1. **基本操作** → `make test-fast` で動作確認
2. **GUI操作** → `make run-gui` で画面操作体験
3. **設定理解** → `config.json` の仕組み理解
4. **Git操作** → push で自動ビルド体験

### よくある質問

**Q: Python初心者ですが大丈夫？**  
A: はい！標準的な開発環境で、段階的に学習できます。

**Q: Windowsに配布するのは面倒？**  
A: GitHub push するだけで自動的に Windows exe が生成されます。

**Q: 環境構築が心配...**  
A: `make setup` 一発で環境構築完了です。

**Q: エラーが出たらどうする？**  
A: ログファイル（`*.log`）とエラーメッセージを確認してください。

## 🎯 主な機能

- **📁 ZIP監視**: ファイルサーバーのZIPを自動監視
- **🏷️ スタンプ追加**: 「済」印を自動追加（日付入り）
- **📄 レイアウト変換**: B5 2面付け自動変換
- **🖨️ 自動印刷**: Windows標準プリンタに送信
- **🖥️ GUI操作**: わかりやすい画面操作
- **📊 ログ機能**: 詳細な処理記録
- **🔧 拡張性**: 様々な便利機能を追加予定

## 🔗 関連ドキュメント

- [`BEGINNER_GUIDE.md`](BEGINNER_GUIDE.md) - 詳細な初心者ガイド
- [`DEVELOPMENT.md`](DEVELOPMENT.md) - 開発者向けガイド  
- [`SETUP_GITHUB.md`](SETUP_GITHUB.md) - GitHubリポジトリ設定手順
- [Python公式チュートリアル](https://docs.python.org/ja/3/tutorial/) - Python学習

## 💪 開発の流れ

### 日常的な開発
```bash
# 1. 開発開始
source venv/bin/activate

# 2. コード編集
# VS Code推奨: code .

# 3. テスト・品質チェック
make test              # 全テスト実行
make lint              # コード品質チェック  
make format            # コードフォーマット

# 4. Git操作
git add .
git commit -m "機能改善"
git push

# 5. リリース作成（exe生成）
# GitHubで新しいリリースを作成 → 自動的にWindows exe生成！
```

### 🚀 便利なコマンド
```bash
make help              # 利用可能コマンド一覧
make test-coverage     # テストカバレッジ測定
make security          # セキュリティチェック
make release-check     # リリース前全チェック
```

**Python初心者に優しい、標準的な開発環境の完成です！** 🎉