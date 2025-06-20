import boto3
import json

def call_claude_bedrock(prompt, max_tokens=1000):
    """
    Amazon Bedrock の Claude を呼び出すシンプルな関数
    
    Args:
        prompt (str): Claude に送信するプロンプト
        max_tokens (int): 最大トークン数
    
    Returns:
        str: Claude からの応答
    """
    
    # Bedrock Runtime クライアントを作成
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'  # 利用可能なリージョンに変更してください
    )
    
    # Claude 3 Haiku のモデル ID
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    
    # リクエストボディを作成
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        # Bedrock API を呼び出し
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType='application/json'
        )
        
        # レスポンスを解析
        response_body = json.loads(response['body'].read())
        
        # Claude の応答テキストを取得
        return response_body['content'][0]['text']
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# 使用例
if __name__ == "__main__":
    # プロンプトを設定
    user_prompt = "こんにちは！今日の天気について教えてください。"
    
    # Claude を呼び出し
    print("Claude に質問中...")
    response = call_claude_bedrock(user_prompt)
    
    if response:
        print("\nClaude の応答:")
        print(response)
    else:
        print("応答を取得できませんでした。")
