# 稟議書チェッカー AWS デプロイガイド

## 🚀 方法1: AWS App Runner (推奨)

### 前提条件
- AWS アカウント
- GitHub アカウント
- AWS CLI 設定済み

### 手順

#### 1. GitHub リポジトリ作成
```bash
# 新しいリポジトリを作成
git init
git add .
git commit -m "Initial commit: 稟議書チェッカー"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ringi-checker.git
git push -u origin main
```

#### 2. AWS App Runner サービス作成
1. AWS コンソールで App Runner を開く
2. 「サービスを作成」をクリック
3. ソース設定:
   - **リポジトリタイプ**: GitHub
   - **リポジトリ**: ringi-checker
   - **ブランチ**: main
   - **設定ファイル**: apprunner.yaml を使用

4. ビルド設定:
   - **ランタイム**: Docker
   - **ビルドコマンド**: 自動検出

5. サービス設定:
   - **サービス名**: ringi-checker
   - **ポート**: 8501
   - **環境変数**:
     - `AWS_DEFAULT_REGION`: us-east-1

6. 「作成とデプロイ」をクリック

#### 3. IAM ロール設定
App Runner サービスに Bedrock アクセス権限を付与:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/anthropic.*",
                "arn:aws:bedrock:*::foundation-model/amazon.nova-*"
            ]
        }
    ]
}
```

## 🐳 方法2: Amazon ECS + Fargate

### 手順

#### 1. ECR リポジトリ作成
```bash
aws ecr create-repository --repository-name ringi-checker --region us-east-1
```

#### 2. Docker イメージビルド・プッシュ
```bash
# ECR ログイン
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# イメージビルド
docker build -t ringi-checker .

# タグ付け
docker tag ringi-checker:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ringi-checker:latest

# プッシュ
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ringi-checker:latest
```

#### 3. ECS クラスター・サービス作成
```bash
# クラスター作成
aws ecs create-cluster --cluster-name ringi-checker-cluster

# タスク定義作成 (task-definition.json を使用)
aws ecs register-task-definition --cli-input-json file://task-definition.json

# サービス作成
aws ecs create-service \
    --cluster ringi-checker-cluster \
    --service-name ringi-checker-service \
    --task-definition ringi-checker-task \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

## 💰 コスト比較

| 方法 | 月額コスト (概算) | 特徴 |
|------|------------------|------|
| App Runner | $25-50 | 最も簡単、自動スケーリング |
| ECS Fargate | $30-60 | 高可用性、細かい制御 |
| EC2 | $20-100 | 完全制御、管理コスト高 |

## 🔒 セキュリティ考慮事項

### 1. 認証・認可
- AWS Cognito でユーザー認証
- IAM ロールベースのアクセス制御

### 2. ネットワークセキュリティ
- VPC 内でのプライベート通信
- セキュリティグループでポート制限
- WAF でアプリケーション保護

### 3. データ保護
- 稟議書データの暗号化
- ログの適切な管理
- 機密情報のマスキング

## 📊 監視・ログ

### CloudWatch 設定
- アプリケーションログ
- メトリクス監視
- アラート設定

### X-Ray トレーシング
- パフォーマンス分析
- エラー追跡

## 🔄 CI/CD パイプライン

GitHub Actions を使用した自動デプロイ:

```yaml
name: Deploy to AWS App Runner

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Deploy to App Runner
      run: |
        aws apprunner start-deployment --service-arn ${{ secrets.APPRUNNER_SERVICE_ARN }}
```

## 🎯 推奨デプロイ方法

**初心者・小規模**: AWS App Runner
**本格運用・大規模**: Amazon ECS + Fargate
**完全制御が必要**: Amazon EC2

どの方法を選択しますか？詳細な手順をサポートします！
