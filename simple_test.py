import streamlit as st

# 最もシンプルなStreamlitアプリ
st.write("# 🎉 App Runner テスト成功！")
st.write("このメッセージが表示されれば、Streamlit は正常に動作しています。")

# 基本的な機能テスト
st.button("テストボタン")
st.text_input("テスト入力")

st.success("✅ 全て正常に動作しています！")
