# 📋 稟議書チェッカー

AI を活用した稟議書の品質チェック・改善提案システム

## 🎯 機能

- **PDFアップロード**: PDFファイルから自動テキスト抽出
- **詳細チェック**: カスタマイズ可能なチェック項目で総合評価
- **改善提案**: 具体的な修正案を提示
- **チェック項目編集**: 組織に応じたカスタマイズ機能
- **複数AIモデル**: Claude & Nova モデル対応

## 🤖 対応AIモデル

- **Claude 3.5 Sonnet**: 最高性能モデル
- **Nova Pro**: Amazon製マルチモーダルモデル
- **Claude 3 Sonnet**: バランス型高性能モデル
- **Claude 3 Haiku**: 高速軽量モデル
- **Nova Lite**: Amazon製軽量モデル
- **Nova Micro**: Amazon製超軽量モデル

## 📊 チェック項目（デフォルト）

1. **基本情報**: 件名、申請者、日付、承認者
2. **内容・目的**: 目的、背景、効果、リスク
3. **予算・コスト**: 予算額、内訳、根拠、ROI
4. **スケジュール**: 実施計画、期限、リソース
5. **文書品質**: 誤字脱字、論理性、構成

## 🚀 ローカル環境での起動

### 前提条件
- Python 3.11以上
- AWS CLI設定済み（Amazon Bedrock アクセス用）

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/nemf/ringi-checker.git
cd ringi-checker

# 仮想環境を作成・有効化
python -m venv claude_env
source claude_env/bin/activate  # Linux/Mac
# または
claude_env\Scripts\activate     # Windows

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーションを起動
streamlit run ringi_checker.py
```

### AWS設定

Amazon Bedrock を使用するため、以下の設定が必要です：

```bash
# AWS認証情報を設定
aws configure

# 必要な権限
# - bedrock:InvokeModel
# - bedrock:ListFoundationModels
```

## 📝 使用方法

1. **PDFアップロード** または **テキスト直接入力**
2. **AIモデルを選択**（サイドバー）
3. **チェック項目をカスタマイズ**（必要に応じて）
4. **「稟議書を詳細チェック」** ボタンをクリック
5. **結果を確認** し、必要に応じてダウンロード

## 🛠️ 技術スタック

- **Frontend**: Streamlit
- **Backend**: Python 3.11+
- **AI**: Amazon Bedrock (Claude & Nova)
- **PDF処理**: PyPDF2, pdfplumber

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。
