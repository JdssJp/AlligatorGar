# AlligatorGar 開発用Makefile

.PHONY: help install install-dev test test-fast test-coverage clean lint format security build setup

# デフォルトターゲット
help: ## ヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# 環境設定
setup: ## 開発環境をセットアップ
	@echo "🛠️  開発環境セットアップ開始..."
	chmod +x setup-ubuntu.sh
	./setup-ubuntu.sh
	@echo "✅ セットアップ完了"

install: ## 本番用依存関係をインストール
	@echo "📦 本番用依存関係インストール..."
	pip install -r requirements.txt

install-dev: ## 開発用依存関係をインストール
	@echo "🔧 開発用依存関係インストール..."
	pip install -r requirements-dev.txt
	@echo "✅ 開発依存関係インストール完了"

# テスト実行
test: ## 全テストを実行
	@echo "🧪 全テスト実行..."
	python3 tests/test_runner.py

test-fast: ## 高速テストのみ実行
	@echo "⚡ 高速テスト実行..."
	python3 -m unittest tests.test_config -v

test-gui: ## GUIテストのみ実行
	@echo "🖥️  GUIテスト実行..."
	python3 -m unittest tests.test_gui -v

test-coverage: ## テストカバレッジ測定
	@echo "📊 テストカバレッジ測定..."
	coverage run -m pytest tests/
	coverage report
	coverage html
	@echo "📈 HTMLレポート: htmlcov/index.html"

# コード品質
lint: ## コード品質チェック
	@echo "🔍 コード品質チェック..."
	flake8 . --statistics || echo "flake8 チェック完了"
	mypy --ignore-missing-imports . || echo "型チェック完了"

format: ## コードフォーマット
	@echo "🎨 コードフォーマット..."
	black .
	isort .
	@echo "✨ フォーマット完了"

security: ## セキュリティチェック
	@echo "🔐 セキュリティチェック..."
	bandit -r . -f json -o bandit-report.json || echo "セキュリティスキャン完了"
	safety check || echo "依存関係セキュリティチェック完了"

# アプリケーション実行
run-gui: ## GUI版を実行
	@echo "🖥️  GUI版起動..."
	python3 gui_main.py

run-console: ## Console版を実行
	@echo "⚫ Console版起動..."
	python3 process_enhanced.py

# テスト用アプリケーション実行
test-basic: ## 基本機能テスト実行
	@echo "🧪 基本機能テスト..."
	python3 test_basic.py

test-pdf: ## PDF処理テスト実行
	@echo "📄 PDF処理テスト..."
	python3 test_pdf_basic.py

test-network: ## ネットワークテスト実行
	@echo "🌐 ネットワークテスト..."
	python3 test_network.py

# ビルド
build: ## アプリケーションをビルド（ローカル）
	@echo "🔨 ローカルビルド..."
	pyinstaller --onefile --windowed --name=AlligatorGar_GUI gui_main.py
	pyinstaller --onefile --console --name=AlligatorGar_Console process_enhanced.py
	@echo "📦 ビルド完了: dist/"

# クリーンアップ
clean: ## 一時ファイルを削除
	@echo "🧹 クリーンアップ..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ *.spec 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml 2>/dev/null || true
	rm -f bandit-report.json 2>/dev/null || true
	@echo "✅ クリーンアップ完了"

# GitHub Actions ローカルテスト（actが必要）
ci-local: ## GitHub Actions をローカルで実行
	@echo "🔄 GitHub Actions ローカル実行..."
	@if command -v act >/dev/null 2>&1; then \
		act -j test; \
	else \
		echo "❌ 'act' がインストールされていません"; \
		echo "インストール: https://github.com/nektos/act"; \
	fi

# 依存関係更新
deps-update: ## 依存関係を更新
	@echo "📦 依存関係更新..."
	pip list --outdated
	@echo "手動で requirements.txt を更新してください"

# 開発環境情報
info: ## 開発環境情報を表示
	@echo "📋 開発環境情報"
	@echo "Python: $(shell python3 --version)"
	@echo "Pip: $(shell pip3 --version)"
	@echo "OS: $(shell uname -s)"
	@echo "ディレクトリ: $(shell pwd)"
	@echo ""
	@echo "📦 インストール済みパッケージ:"
	@pip3 list | grep -E "(PyMuPDF|Pillow|reportlab|tkinter|pytest|coverage|flake8|black)" || echo "主要パッケージが見つかりません"

# リリース準備
release-check: ## リリース前チェック
	@echo "🚀 リリース前チェック..."
	$(MAKE) clean
	$(MAKE) lint
	$(MAKE) test-coverage
	$(MAKE) security
	@echo ""
	@echo "✅ リリース準備チェック完了"
	@echo "📝 次のステップ:"
	@echo "   1. git add ."
	@echo "   2. git commit -m 'リリース準備'"
	@echo "   3. git push"
	@echo "   4. GitHubでリリース作成"