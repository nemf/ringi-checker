#!/bin/bash

# 依存関係のインストール
echo "依存関係をインストール中..."
pip install -r requirements.txt

# Streamlit アプリを起動
echo "Streamlit アプリを起動中..."
streamlit run streamlit_claude_app.py
