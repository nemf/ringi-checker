import streamlit as st

st.title("🚀 App Runner テスト")
st.write("このページが表示されれば、App Runner は正常に動作しています！")

st.success("✅ デプロイ成功！")

# 環境変数の確認
import os
st.write("### 環境変数")
st.write(f"AWS_DEFAULT_REGION: {os.environ.get('AWS_DEFAULT_REGION', 'Not set')}")
st.write(f"PORT: {os.environ.get('PORT', 'Not set')}")

# 簡単な機能テスト
name = st.text_input("お名前を入力してください")
if name:
    st.write(f"こんにちは、{name}さん！")
