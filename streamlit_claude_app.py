import streamlit as st
import boto3
import json
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="Claude Chat",
    page_icon="🤖",
    layout="wide"
)

# モデル設定
CLAUDE_MODELS = {
    "Claude 3.5 Sonnet": {
        "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "description": "最高性能モデル - 複雑なタスクに最適",
        "max_tokens": 8000,
        "icon": "🧠",
        "provider": "Anthropic"
    },
    "Claude 3 Sonnet": {
        "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
        "description": "高性能モデル - バランスの取れた性能",
        "max_tokens": 4000,
        "icon": "🎯",
        "provider": "Anthropic"
    },
    "Claude 3 Haiku": {
        "model_id": "anthropic.claude-3-haiku-20240307-v1:0", 
        "description": "高速・軽量モデル - 簡単なタスクに最適",
        "max_tokens": 4000,
        "icon": "⚡",
        "provider": "Anthropic"
    },
    "Nova Pro": {
        "model_id": "amazon.nova-pro-v1:0",
        "description": "Amazon最高性能 - マルチモーダル対応",
        "max_tokens": 5000,
        "icon": "🚀",
        "provider": "Amazon"
    },
    "Nova Lite": {
        "model_id": "amazon.nova-lite-v1:0",
        "description": "Amazon軽量モデル - 高速処理",
        "max_tokens": 4000,
        "icon": "💫",
        "provider": "Amazon"
    },
    "Nova Micro": {
        "model_id": "amazon.nova-micro-v1:0",
        "description": "Amazon超軽量 - 基本タスク用",
        "max_tokens": 3000,
        "icon": "⭐",
        "provider": "Amazon"
    }
}

def initialize_bedrock_client():
    """Bedrock Runtime クライアントを初期化"""
    try:
        return boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'  # 必要に応じて変更
        )
    except Exception as e:
        st.error(f"AWS 接続エラー: {e}")
        return None

def call_claude(client, model_id, prompt, max_tokens=4000, temperature=0.7):
    """Claude を呼び出す"""
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        st.error(f"Claude 呼び出しエラー: {e}")
        return None

def call_nova(client, model_id, prompt, max_tokens=4000, temperature=0.7):
    """Amazon Nova を呼び出す"""
    
    body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "max_new_tokens": max_tokens,
            "temperature": temperature
        }
    }
    
    try:
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['output']['message']['content'][0]['text']
        
    except Exception as e:
        st.error(f"Nova 呼び出しエラー: {e}")
        return None

def call_model(client, model_id, provider, prompt, max_tokens=4000, temperature=0.7):
    """プロバイダーに応じてモデルを呼び出す"""
    if provider == "Anthropic":
        return call_claude(client, model_id, prompt, max_tokens, temperature)
    elif provider == "Amazon":
        return call_nova(client, model_id, prompt, max_tokens, temperature)
    else:
        st.error(f"サポートされていないプロバイダー: {provider}")
        return None

def main():
    # タイトル
    st.title("🤖 AI Chat - Claude & Nova")
    st.markdown("---")
    
    # サイドバー設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # モデル選択
        st.subheader("🎯 モデル選択")
        selected_model = st.selectbox(
            "使用するモデル",
            options=list(CLAUDE_MODELS.keys()),
            format_func=lambda x: f"{CLAUDE_MODELS[x]['icon']} {x}",
            help="用途に応じてモデルを選択してください"
        )
        
        # 選択されたモデルの情報表示
        model_info = CLAUDE_MODELS[selected_model]
        st.info(f"**{selected_model}** ({model_info['provider']})\n\n{model_info['description']}")
        
        st.markdown("---")
        
        # パラメータ設定
        st.subheader("🔧 パラメータ")
        max_tokens = st.slider(
            "最大トークン数", 
            100, 
            model_info['max_tokens'], 
            min(4000, model_info['max_tokens'])
        )
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        st.markdown("---")
        
        # 統計情報
        if 'messages' in st.session_state and st.session_state.messages:
            st.subheader("📊 統計")
            user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
            assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
            st.metric("質問数", user_messages)
            st.metric("回答数", assistant_messages)
        
        st.markdown("---")
        
        # 会話履歴クリア
        if st.button("🗑️ 会話履歴をクリア", type="secondary"):
            st.session_state.messages = []
            st.rerun()
    
    # Bedrock クライアント初期化
    if 'bedrock_client' not in st.session_state:
        st.session_state.bedrock_client = initialize_bedrock_client()
    
    if st.session_state.bedrock_client is None:
        st.error("AWS Bedrock に接続できません。認証情報を確認してください。")
        st.info("以下のコマンドで認証情報を設定してください：\n```bash\naws configure\n```")
        return
    
    # 現在のモデル表示
    st.info(f"現在使用中: {CLAUDE_MODELS[selected_model]['icon']} **{selected_model}** ({CLAUDE_MODELS[selected_model]['provider']})")
    
    # 会話履歴の初期化
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 会話履歴の表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"送信時刻: {message['timestamp']}")
            if "model" in message and message["role"] == "assistant":
                st.caption(f"使用モデル: {message['model']}")
    
    # ユーザー入力
    if prompt := st.chat_input("Claude に質問してください..."):
        # ユーザーメッセージを履歴に追加
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": timestamp
        })
        
        # ユーザーメッセージを表示
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"送信時刻: {timestamp}")
        
        # Claude の応答を取得・表示
        with st.chat_message("assistant"):
            with st.spinner(f"{selected_model} が考えています..."):
                response = call_model(
                    st.session_state.bedrock_client, 
                    model_info['model_id'],
                    model_info['provider'],
                    prompt, 
                    max_tokens, 
                    temperature
                )
            
            if response:
                st.markdown(response)
                response_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.caption(f"応答時刻: {response_timestamp}")
                st.caption(f"使用モデル: {selected_model}")
                
                # アシスタントメッセージを履歴に追加
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "timestamp": response_timestamp,
                    "model": selected_model
                })
            else:
                st.error("応答を取得できませんでした。")
    
    # フッター
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            Powered by Amazon Bedrock | Claude & Nova Models
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
