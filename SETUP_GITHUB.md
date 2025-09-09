# 🐊 AlligatorGar - GitHub リポジトリセットアップ

## 📋 リポジトリ作成手順

### 1. GitHubでリポジトリ作成
1. https://github.com/jdssjp にログイン
2. **New repository** クリック
3. リポジトリ設定:
   - **Repository name**: `AlligatorGar`
   - **Description**: `🐊 強力な多機能自動化ツール - PDF処理・スタンプ・印刷自動化`
   - **Public** を選択
   - **Add a README file** は**チェックしない**（既にある）
   - **Add .gitignore** は**チェックしない**（既にある）

### 2. ローカルでGit初期化
```bash
# 現在のディレクトリで実行
git init
git add .
git commit -m "🐊 初回コミット: AlligatorGar多機能自動化ツール"

# リモートリポジトリ追加
git branch -M main
git remote add origin https://github.com/jdssjp/AlligatorGar.git
git push -u origin main
```

### 3. 初回リリース作成
1. GitHubリポジトリページに移動
2. **Releases** → **Create a new release**
3. リリース設定:
   - **Tag version**: `v1.0.0`
   - **Release title**: `🐊 AlligatorGar v1.0.0 - 初回リリース`
   - **Description**:
     ```
     ## 🐊 AlligatorGar - 強力な多機能自動化ツール 初回リリース
     
     PDF処理自動化システムの完全版です。
     
     ### ✨ 主な機能
     - 📁 ZIP ファイル自動監視
     - 🏷️ PDF スタンプ追加（日付入り「済」印）
     - 📄 B5 2面付けレイアウト変換
     - 🖨️ 自動印刷・保存
     - 🖥️ GUI版 + Console版の両対応
     
     ### 📥 ダウンロード
     - **GUI版**: `AlligatorGar_GUI.exe` (初心者推奨)
     - **Console版**: `AlligatorGar_Console.exe` (サーバー・上級者向け)
     
     ### 💻 動作環境
     - Windows 10/11 (32bit/64bit対応)
     - Python環境不要
     - 管理者権限不要
     
     ### 🎯 使用方法
     1. exe ファイルをダウンロード
     2. ダブルクリックで実行
     3. GUI版なら画面の指示に従って設定
     
     初回リリースです。ご意見・ご要望をお聞かせください！
     ```
4. **Publish release** クリック

### 4. 自動ビルド確認
- リリース作成と同時にGitHub Actionsが開始
- **Actions** タブで進行状況確認
- 完了後、リリースページに実行ファイルが自動追加

## 🔄 今後の開発フロー

### 日常的な開発
```bash
# 機能追加・改善
git add .
git commit -m "機能追加: XXX"
git push
```

### 新バージョンリリース
1. コードをpush
2. GitHubで新しいリリースを作成
3. 自動的にWindows実行ファイル生成・添付

## 🎯 リリースバージョニング
- **v1.0.0**: 初回リリース（PDF処理システム）
- **v1.1.0**: 機能追加
- **v1.0.1**: バグフィックス
- **v2.0.0**: 大幅な機能拡張（新しい自動化機能追加時）

## 📝 注意事項
- リリースを作成すると自動的にWindows exeがビルド・添付されます
- 開発中のpushではビルドされません（リソース節約）
- 手動でビルドしたい場合は**Actions** → **AlligatorGar Auto Build** → **Run workflow**