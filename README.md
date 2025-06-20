# 📋 稟議書チェッカー

AI を活用した稟議書の品質チェック・改善提案システム

## 🎯 機能

- **PDFアップロード**: PDFファイルから自動テキスト抽出
- **詳細チェック**: 5つのカテゴリで総合評価
- **改善提案**: 具体的な修正案を提示
- **カスタマイズ**: チェック項目の編集機能
- **複数AIモデル**: Claude & Nova モデル対応

## 🤖 対応AIモデル

- **Claude 3.5 Sonnet**: 最高性能モデル
- **Nova Pro**: Amazon製マルチモーダルモデル
- **Claude 3 Sonnet**: バランス型高性能モデル
- **Claude 3 Haiku**: 高速軽量モデル
- **Nova Lite**: Amazon製軽量モデル
- **Nova Micro**: Amazon製超軽量モデル

## 📊 チェック項目

1. **基本情報**: 件名、申請者、日付、承認者
2. **内容・目的**: 目的、背景、効果、リスク
3. **予算・コスト**: 予算額、内訳、根拠、ROI
4. **スケジュール**: 実施計画、期限、リソース
5. **文書品質**: 誤字脱字、論理性、構成

## 🚀 デプロイ

このアプリケーションは AWS App Runner でデプロイされています。

### 必要な AWS サービス
- Amazon Bedrock (Claude & Nova モデル)
- AWS App Runner
- Amazon ECR (コンテナレジストリ)

### 環境変数
- `AWS_DEFAULT_REGION`: us-east-1

## 🔒 セキュリティ

- AWS IAM ロールベースのアクセス制御
- Amazon Bedrock の安全なAPI呼び出し
- 稟議書データの適切な処理

## 📝 使用方法

1. PDFファイルをアップロードまたはテキストを直接入力
2. AIモデルを選択
3. 「稟議書を詳細チェック」ボタンをクリック
4. 結果を確認し、必要に応じてダウンロード

## 🛠️ 技術スタック

- **Frontend**: Streamlit
- **Backend**: Python 3.12
- **AI**: Amazon Bedrock (Claude & Nova)
- **PDF処理**: PyPDF2, pdfplumber
- **デプロイ**: AWS App Runner
- **コンテナ**: Docker

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。
