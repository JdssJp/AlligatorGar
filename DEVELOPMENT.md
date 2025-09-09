# 🐊 AlligatorGar 開発ガイド

## 📋 開発環境セットアップ

### 必須要件
- Python 3.8+ 
- Git
- make (GNU Make)

### セットアップ手順

```bash
# 1. リポジトリクローン
git clone https://github.com/jdssjp/AlligatorGar.git
cd AlligatorGar

# 2. 開発環境自動セットアップ
make setup

# 3. 開発用依存関係インストール
make install-dev

# 4. 開発環境情報確認
make info
```

## 🧪 テスト実行

### 基本テスト

```bash
# 全テスト実行
make test

# 高速テスト（設定関連のみ）
make test-fast

# GUIテストのみ
make test-gui

# テストカバレッジ測定
make test-coverage
```

### 個別テスト実行

```bash
# 特定のテストモジュール
python3 -m unittest tests.test_config -v
python3 -m unittest tests.test_gui -v
python3 -m unittest tests.test_pdf_processing -v

# pytest使用
pytest tests/test_config.py -v
pytest tests/ -k "cross_platform"
```

## 🎨 コード品質

### フォーマット・リンティング

```bash
# コードフォーマット自動実行
make format

# コード品質チェック
make lint

# セキュリティチェック
make security
```

### Pre-commitフック

```bash
# pre-commit設定
pre-commit install

# 手動実行
pre-commit run --all-files
```

## 🚀 アプリケーション実行

### 開発時実行

```bash
# GUI版起動
make run-gui

# Console版起動  
make run-console

# 基本機能テスト
make test-basic
```

### 個別機能テスト

```bash
# PDF処理テスト
make test-pdf

# ネットワークテスト
make test-network
```

## 🔨 ビルド・リリース

### ローカルビルド

```bash
# 実行ファイル生成（要PyInstaller）
make build

# 生成物確認
ls -la dist/
```

### リリース前チェック

```bash
# 完全チェック実行
make release-check
```

## 📁 プロジェクト構造

```
AlligatorGar/
├── 🐍 メインプログラム
│   ├── gui_main.py              # GUI版アプリケーション
│   └── process_enhanced.py      # Console版アプリケーション
│
├── 🧪 テストスイート
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_config.py      # 設定機能テスト
│   │   ├── test_gui.py         # GUI機能テスト  
│   │   ├── test_pdf_processing.py # PDF処理テスト
│   │   └── test_runner.py      # テストランナー
│   │
├── ⚙️  開発環境設定
│   ├── requirements.txt        # 本番依存関係
│   ├── requirements-dev.txt    # 開発依存関係
│   ├── pyproject.toml         # モダンPython設定
│   ├── pytest.ini            # pytest設定
│   ├── .coveragerc           # カバレッジ設定
│   ├── Makefile              # 開発タスクランナー
│   ├── .pre-commit-config.yaml # pre-commitフック
│   └── setup-ubuntu.sh       # Ubuntu環境セットアップ
│
├── 🔄 CI/CD
│   └── .github/
│       ├── workflows/
│       │   ├── ci.yml         # CI テストワークフロー
│       │   └── build-simple.yml # Windows exe ビルド
│       └── dependabot.yml     # 依存関係自動更新
│
├── 📚 ドキュメント
│   ├── README.md              # プロジェクト概要
│   ├── DEVELOPMENT.md         # このファイル（開発者向け）
│   ├── BEGINNER_GUIDE.md      # 初心者向けガイド
│   ├── SETUP_GITHUB.md        # GitHub設定手順
│   └── CLAUDE.md              # Claude Code向け開発メモ
│
└── 🗑️  除外ファイル
    ├── .gitignore            # Git除外設定
    ├── .python-version       # Python バージョン固定
    ├── venv/                 # 仮想環境（除外）
    └── __pycache__/          # Pythonキャッシュ（除外）
```

## 📊 テスト戦略

### テスト分類

1. **ユニットテスト** (Unit Tests)
   - 個別機能の動作確認
   - モックを使用した依存関係分離
   - 高速実行

2. **統合テスト** (Integration Tests)  
   - コンポーネント間の連携確認
   - 実際のファイル操作
   - GUI動作確認

3. **クロスプラットフォームテスト**
   - Windows/Linux/macOS対応確認
   - OS固有機能の適切な分岐
   - 警告メッセージの表示

### テストマーカー

```python
import pytest

@pytest.mark.unit
def test_config_creation():
    # ユニットテスト

@pytest.mark.gui  
def test_window_creation():
    # GUIテスト

@pytest.mark.windows_only
def test_print_functionality():
    # Windows専用機能テスト
```

## 🐛 デバッグ・トラブルシューティング

### よくある問題

1. **依存関係エラー**
   ```bash
   # 仮想環境確認
   which python3
   pip3 list | grep -E "(PyMuPDF|Pillow|reportlab)"
   
   # 再インストール
   make clean
   make setup
   ```

2. **テスト失敗**
   ```bash
   # 詳細実行
   python3 -m unittest tests.test_config.TestConfig.test_default_config_creation -v
   
   # デバッグモード
   python3 -m pdb -m unittest tests.test_config
   ```

3. **GUI起動エラー**
   ```bash
   # tkinter確認
   python3 -c "import tkinter; print('tkinter OK')"
   
   # システム依存関係
   sudo apt install python3-tk  # Ubuntu
   ```

## 📈 パフォーマンス最適化

### テスト実行の高速化

```bash
# 並列テスト実行
pytest tests/ -n auto

# 特定テストのみ
pytest tests/ -k "not slow"

# 変更されたファイルのみ
pytest --lf  # last failed
pytest --ff  # failed first
```

### メモリ使用量最適化

- PDF処理時のメモリリークチェック
- 大量ファイル処理のバッチサイズ調整
- GUI更新頻度の最適化

## 🔐 セキュリティ

### セキュリティチェック

```bash
# 脆弱性スキャン
make security

# 手動チェック
bandit -r . -f json
safety check
```

### セキュアコーディング

- ファイルパスのサニタイズ
- 外部コマンド実行時の引数検証  
- 設定ファイルの権限管理

## 📝 コントリビューション

### プルリクエスト手順

1. Forkリポジトリ作成
2. 機能ブランチ作成 (`git checkout -b feature/new-feature`)
3. 変更・テスト実装
4. コード品質チェック (`make release-check`)
5. プルリクエスト作成

### コーディング規約

- **フォーマット**: Black (line-length=88)
- **インポート順序**: isort (profile=black)
- **リンティング**: flake8, pylint
- **型ヒント**: mypy推奨
- **ドキュメント**: docstring必須

## 🔄 継続的インテグレーション

### GitHub Actions

- **CI Tests**: プルリクエスト時の自動テスト
- **Build**: リリース時のWindows exe自動生成
- **Security**: 定期的なセキュリティスキャン

### Dependabot

- 週次依存関係更新チェック
- セキュリティアップデート自動適用
- グループ化による効率的更新

## 📞 サポート

### 問題報告

- [GitHub Issues](https://github.com/jdssjp/AlligatorGar/issues)
- バグレポート時は実行環境情報を含める (`make info`)

### 開発者向けコミュニケーション

- 重大な変更は事前にIssueで議論
- 新機能提案はDiscussion推奨

---

**Happy Coding! 🐊**