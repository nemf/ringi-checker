#!/bin/bash

# 仮想環境が存在しない場合は作成
if [ ! -d "claude_env" ]; then
    echo "仮想環境を作成中..."
    python3 -m venv claude_env
fi

# 仮想環境を有効化
echo "仮想環境を有効化中..."
source claude_env/bin/activate

# 依存関係のインストール
echo "依存関係をインストール中..."
pip install -r requirements.txt

# 稟議書チェッカーアプリを起動
echo "稟議書チェッカーを起動中..."
streamlit run ringi_checker.py --server.port 8502 --server.address 0.0.0.0
