import streamlit as st
import boto3
import json
from datetime import datetime
import re
import PyPDF2
import pdfplumber
import io
import os

# ページ設定
st.set_page_config(
    page_title="稟議書チェッカー",
    page_icon="📋",
    layout="wide"
)

# モデル設定
MODELS = {
    "Claude 3.5 Sonnet": {
        "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "description": "最高性能 - 詳細な分析に最適",
        "max_tokens": 8000,
        "icon": "🧠",
        "provider": "Anthropic"
    },
    "Nova Pro": {
        "model_id": "amazon.nova-pro-v1:0",
        "description": "Amazon最高性能 - 総合的な分析",
        "max_tokens": 5000,
        "icon": "🚀",
        "provider": "Amazon"
    },
    "Claude 3 Haiku": {
        "model_id": "anthropic.claude-3-haiku-20240307-v1:0", 
        "description": "高速チェック - 基本的な確認",
        "max_tokens": 4000,
        "icon": "⚡",
        "provider": "Anthropic"
    }
}

# 稟議書チェック項目（デフォルト）
DEFAULT_CHECK_ITEMS = {
    "基本情報": [
        "件名が明確で具体的か",
        "申請者・部署が明記されているか",
        "申請日が記載されているか",
        "承認者が適切に設定されているか"
    ],
    "内容・目的": [
        "申請の目的が明確に記載されているか",
        "背景・理由が十分に説明されているか",
        "期待される効果・メリットが記載されているか",
        "リスクや課題が検討されているか"
    ],
    "予算・コスト": [
        "予算額が明確に記載されているか",
        "費用の内訳が詳細に記載されているか",
        "予算根拠が合理的か",
        "ROI（投資対効果）が検討されているか"
    ],
    "スケジュール": [
        "実施スケジュールが明確か",
        "各フェーズの期限が設定されているか",
        "リソース配分が適切か",
        "遅延リスクが考慮されているか"
    ],
    "文書品質": [
        "誤字脱字がないか",
        "文章が分かりやすいか",
        "論理的な構成になっているか",
        "必要な添付資料があるか"
    ]
}

def initialize_check_items():
    """チェック項目を初期化"""
    if 'check_items' not in st.session_state:
        st.session_state.check_items = DEFAULT_CHECK_ITEMS.copy()
    return st.session_state.check_items

def save_check_items_to_file(check_items, filename="custom_check_items.json"):
    """チェック項目をファイルに保存"""
    try:
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(check_items, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存エラー: {e}")
        return False

def load_check_items_from_file(filename="custom_check_items.json"):
    """ファイルからチェック項目を読み込み"""
    try:
        import json
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None

def extract_text_from_pdf(pdf_file):
    """PDFファイルからテキストを抽出"""
    try:
        # pdfplumberを使用してテキスト抽出（より高精度）
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            return text.strip()
        
        # pdfplumberで抽出できない場合はPyPDF2を試行
        pdf_file.seek(0)  # ファイルポインタをリセット
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        return text.strip() if text.strip() else None
        
    except Exception as e:
        st.error(f"PDF読み込みエラー: {e}")
        return None

def clean_extracted_text(text):
    """抽出されたテキストをクリーンアップ"""
    if not text:
        return ""
    
    # 不要な改行や空白を整理
    text = re.sub(r'\n\s*\n', '\n\n', text)  # 複数の空行を2行に
    text = re.sub(r'[ \t]+', ' ', text)      # 複数のスペース・タブを1つに
    text = text.strip()
    
    return text

def initialize_bedrock_client():
    """Bedrock Runtime クライアントを初期化"""
    try:
        return boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'
        )
    except Exception as e:
        st.error(f"AWS 接続エラー: {e}")
        return None
    """Bedrock Runtime クライアントを初期化"""
    try:
        return boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'
        )
    except Exception as e:
        st.error(f"AWS 接続エラー: {e}")
        return None

def call_claude(client, model_id, prompt, max_tokens=4000, temperature=0.3):
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

def call_nova(client, model_id, prompt, max_tokens=4000, temperature=0.3):
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

def call_model(client, model_id, provider, prompt, max_tokens=4000, temperature=0.3):
    """プロバイダーに応じてモデルを呼び出す"""
    if provider == "Anthropic":
        return call_claude(client, model_id, prompt, max_tokens, temperature)
    elif provider == "Amazon":
        return call_nova(client, model_id, prompt, max_tokens, temperature)
    else:
        st.error(f"サポートされていないプロバイダー: {provider}")
        return None

def create_check_prompt(ringi_text, check_items):
    """稟議書チェック用のプロンプトを作成（詳細チェックのみ）"""
    
    # チェック項目をプロンプト用に整形
    check_items_text = ""
    for category, items in check_items.items():
        check_items_text += f"\n{category}:\n"
        for item in items:
            check_items_text += f"- {item}\n"
    
    prompt = f"""
以下の稟議書を詳細にチェックし、改善提案を行ってください。

【稟議書内容】
{ringi_text}

【チェック観点】
{check_items_text}

【出力形式】
## 📊 総合評価・最終判定
- **評価点数**: X/100点
- **承認可否**: ○（承認可）/ △（条件付き承認）/ ×（承認不可）
- **判定理由**: [承認可否の根拠]
- **総合コメント**: [全体的な評価と印象]

### 📈 カテゴリ別評価（5段階）
"""
    
    # 各カテゴリの5段階評価を動的に生成
    for category in check_items.keys():
        prompt += f"- **{category}**: ⭐⭐⭐⭐⭐ (X/5) - [簡潔な評価コメント]\n"
    
    prompt += """
## ✅ 良い点
- [具体的な良い点を列挙]

## ⚠️ 改善が必要な点
- [具体的な問題点を列挙]

## 💡 具体的な改善提案
- [実行可能な改善案を提示]

## 📋 チェック項目別詳細評価

"""
    
    # 各カテゴリの詳細評価セクションを動的に生成
    total_categories = len(check_items)
    points_per_category = 100 // total_categories
    remaining_points = 100 % total_categories
    
    for i, (category, items) in enumerate(check_items.items()):
        # 最後のカテゴリに余りの点数を加算
        category_points = points_per_category + (remaining_points if i == total_categories - 1 else 0)
        
        prompt += f"""### {category} (X/{category_points}点)
**該当部分の抜粋**:
```
[稟議書から該当する部分を抜粋]
```

**評価根拠**:
- [なぜこの点数なのかの理由]

**推奨修正案**:
- [具体的な修正提案]

"""
    
    prompt += """## 🚨 重要な指摘事項
- [承認に影響する重要な問題点]

## 📝 修正版サンプル（重要部分のみ）
```
[最も重要な修正箇所について、修正後のサンプルテキストを提示]
```

必ず最初の総合評価で承認可否と各カテゴリの5段階評価（⭐で表現）を含めてください。
"""
    
    return prompt

def main():
    # タイトル
    st.title("📋 稟議書チェッカー")
    st.markdown("AI を活用して稟議書の品質をチェックし、改善提案を行います")
    st.markdown("---")
    
    # チェック項目を初期化
    check_items = initialize_check_items()
    
    # サイドバー設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # チェック項目編集
        st.subheader("📋 チェック項目設定")
        
        # チェック項目編集モード
        edit_mode = st.checkbox("✏️ チェック項目を編集", help="独自のチェック項目を設定できます")
        
        if edit_mode:
            st.markdown("### チェック項目編集")
            
            # 既存カテゴリの編集
            categories_to_delete = []
            for category in list(check_items.keys()):
                with st.expander(f"📂 {category}"):
                    # カテゴリ名編集
                    new_category_name = st.text_input(
                        "カテゴリ名",
                        value=category,
                        key=f"cat_{category}"
                    )
                    
                    # 項目編集
                    items = check_items[category].copy()
                    items_to_delete = []
                    
                    for i, item in enumerate(items):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            new_item = st.text_input(
                                f"項目 {i+1}",
                                value=item,
                                key=f"item_{category}_{i}"
                            )
                            items[i] = new_item
                        with col2:
                            if st.button("🗑️", key=f"del_item_{category}_{i}", help="項目を削除"):
                                items_to_delete.append(i)
                    
                    # 項目削除処理
                    for i in sorted(items_to_delete, reverse=True):
                        items.pop(i)
                    
                    # 新しい項目追加
                    if st.button(f"➕ 項目追加", key=f"add_item_{category}"):
                        items.append("新しいチェック項目")
                    
                    # カテゴリ削除ボタン
                    if st.button(f"🗑️ {category}カテゴリを削除", key=f"del_cat_{category}"):
                        categories_to_delete.append(category)
                    
                    # 変更を反映
                    if new_category_name != category:
                        check_items[new_category_name] = items
                        categories_to_delete.append(category)
                    else:
                        check_items[category] = items
            
            # カテゴリ削除処理
            for category in categories_to_delete:
                if category in check_items:
                    del check_items[category]
            
            # 新しいカテゴリ追加
            st.markdown("### 新しいカテゴリ追加")
            col1, col2 = st.columns([3, 1])
            with col1:
                new_category = st.text_input("新しいカテゴリ名", placeholder="例: コンプライアンス")
            with col2:
                if st.button("➕ カテゴリ追加") and new_category:
                    if new_category not in check_items:
                        check_items[new_category] = ["新しいチェック項目"]
                        st.success(f"カテゴリ '{new_category}' を追加しました")
                        st.rerun()
            
            # 設定の保存・読み込み
            st.markdown("### 設定の保存・読み込み")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 設定を保存"):
                    if save_check_items_to_file(check_items):
                        st.success("設定を保存しました")
            
            with col2:
                if st.button("📂 設定を読み込み"):
                    loaded_items = load_check_items_from_file()
                    if loaded_items:
                        st.session_state.check_items = loaded_items
                        st.success("設定を読み込みました")
                        st.rerun()
            
            with col3:
                if st.button("🔄 デフォルトに戻す"):
                    st.session_state.check_items = DEFAULT_CHECK_ITEMS.copy()
                    st.success("デフォルト設定に戻しました")
                    st.rerun()
            
            # セッションに保存
            st.session_state.check_items = check_items
        
        else:
            # チェック項目表示（編集モードでない場合）
            for category, items in check_items.items():
                with st.expander(f"**{category}**"):
                    for item in items:
                        st.write(f"• {item}")
        
        # チェック項目統計
        total_items = sum(len(items) for items in check_items.values())
        st.caption(f"📊 総チェック項目数: {total_items}項目 ({len(check_items)}カテゴリ)")
        
        st.markdown("---")
        
        # モデル選択
        st.subheader("🤖 AIモデル選択")
        selected_model = st.selectbox(
            "使用するモデル",
            options=list(MODELS.keys()),
            format_func=lambda x: f"{MODELS[x]['icon']} {x}",
            help="用途に応じてモデルを選択してください"
        )
        
        model_info = MODELS[selected_model]
        st.info(f"**{selected_model}** ({model_info['provider']})\n\n{model_info['description']}")
    
    # Bedrock クライアント初期化
    if 'bedrock_client' not in st.session_state:
        st.session_state.bedrock_client = initialize_bedrock_client()
    
    if st.session_state.bedrock_client is None:
        st.error("AWS Bedrock に接続できません。認証情報を確認してください。")
        st.info("以下のコマンドで認証情報を設定してください：\n```bash\naws configure\n```")
        return
    
    # メインコンテンツ - 稟議書入力
    st.subheader("📝 稟議書入力")
    
    # 入力方法選択
    input_method = st.radio(
        "入力方法を選択",
        ["📄 PDFアップロード", "✏️ テキスト入力"],
        horizontal=True
    )
    
    ringi_text = ""
    
    if input_method == "📄 PDFアップロード":
        st.markdown("### PDFファイルをアップロード")
        uploaded_file = st.file_uploader(
            "稟議書のPDFファイルを選択してください",
            type=['pdf'],
            help="PDFファイルからテキストを自動抽出します"
        )
        
        if uploaded_file is not None:
            # ファイル情報表示
            st.info(f"📁 ファイル名: {uploaded_file.name}")
            st.info(f"📊 ファイルサイズ: {uploaded_file.size:,} bytes")
            
            # PDFからテキスト抽出
            with st.spinner("PDFからテキストを抽出中..."):
                extracted_text = extract_text_from_pdf(uploaded_file)
            
            if extracted_text:
                cleaned_text = clean_extracted_text(extracted_text)
                ringi_text = cleaned_text
                
                # 抽出結果のプレビュー
                with st.expander("📖 抽出されたテキストのプレビュー"):
                    st.text_area(
                        "抽出されたテキスト",
                        value=ringi_text[:1000] + "..." if len(ringi_text) > 1000 else ringi_text,
                        height=200,
                        disabled=True
                    )
                    st.caption(f"総文字数: {len(ringi_text)} 文字")
                
                # テキスト編集オプション
                if st.checkbox("📝 抽出されたテキストを編集する"):
                    ringi_text = st.text_area(
                        "テキストを編集",
                        value=ringi_text,
                        height=300,
                        help="必要に応じて抽出されたテキストを修正してください"
                    )
            else:
                st.error("PDFからテキストを抽出できませんでした。手動でテキストを入力してください。")
    
    else:  # テキスト入力
        st.markdown("### テキスト入力")
        
        # サンプル稟議書ボタン
        if st.button("📄 サンプル稟議書を読み込み"):
            sample_text = """件名: 新規CRMシステム導入に関する稟議

申請者: 営業部 田中太郎
申請日: 2024年6月20日
承認者: 営業部長、IT部長、取締役

【目的】
顧客管理の効率化と営業活動の最適化を図るため、新規CRMシステムを導入したい。

【背景】
現在の顧客管理は Excel ベースで行っており、以下の課題がある：
- 顧客情報の重複や不整合
- 営業活動の進捗が見えにくい
- レポート作成に時間がかかる

【導入予定システム】
- システム名: SalesForce Professional
- 初期費用: 500万円
- 月額費用: 50万円（100ユーザー）

【期待効果】
- 営業効率20%向上
- 顧客満足度向上
- データ分析による戦略立案

【スケジュール】
- 2024年7月: システム選定完了
- 2024年8月: 導入開始
- 2024年10月: 運用開始

以上、ご承認のほどよろしくお願いいたします。"""
            st.session_state.ringi_text = sample_text
        
        # 稟議書テキスト入力
        ringi_text = st.text_area(
            "稟議書の内容を入力してください",
            value=st.session_state.get('ringi_text', ''),
            height=400,
            help="稟議書の全文を貼り付けてください"
        )
    
    # 文字数表示
    if ringi_text:
        st.caption(f"📊 文字数: {len(ringi_text)} 文字")
        
        # 長すぎる場合の警告
        if len(ringi_text) > 10000:
            st.warning("⚠️ テキストが長すぎます。処理に時間がかかる可能性があります。")
    
    # チェック実行ボタン
    check_button = st.button(
        "🔍 稟議書を詳細チェック",
        type="primary",
        disabled=not ringi_text.strip(),
        help="稟議書の内容をAIが詳細に分析します"
    )
    
    # チェック結果表示（下に配置）
    if check_button and ringi_text.strip():
        st.markdown("---")
        st.subheader("📊 チェック結果")
        
        # プロンプト作成
        prompt = create_check_prompt(ringi_text, check_items)
        
        # AI分析実行
        with st.spinner(f"{selected_model} が稟議書を分析中..."):
            result = call_model(
                st.session_state.bedrock_client,
                model_info['model_id'],
                model_info['provider'],
                prompt,
                model_info['max_tokens'],
                0.3  # 低めのtemperatureで一貫性を重視
            )
        
        if result:
            # 結果表示
            st.markdown(result)
            
            # 結果の要約を抽出して表示
            if "評価点数" in result or "評価:" in result:
                # 評価点数を抽出
                score_match = re.search(r'(\d+)/100点', result)
                if score_match:
                    score = int(score_match.group(1))
                    
                    # スコアに応じた色分け
                    if score >= 80:
                        score_color = "🟢"
                        status = "優秀"
                    elif score >= 60:
                        score_color = "🟡"
                        status = "良好"
                    elif score >= 40:
                        score_color = "🟠"
                        status = "要改善"
                    else:
                        score_color = "🔴"
                        status = "要大幅改善"
                    
                    st.success(f"{score_color} **総合評価: {score}/100点 ({status})**")
            
            # 承認可否を抽出して表示
            approval_match = re.search(r'承認可否[：:]\s*([○△×])', result)
            if approval_match:
                approval = approval_match.group(1)
                if approval == "○":
                    st.success("✅ **承認可**: この稟議書は承認可能です")
                elif approval == "△":
                    st.warning("⚠️ **条件付き承認**: 修正後に承認可能です")
                else:
                    st.error("❌ **承認不可**: 大幅な修正が必要です")
            
            # 結果をセッションに保存
            st.session_state.last_result = {
                'text': result,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'model': selected_model,
                'input_method': input_method,
                'char_count': len(ringi_text),
                'score': score_match.group(1) if score_match else "N/A",
                'approval': approval_match.group(1) if approval_match else "N/A"
            }
            
            # ダウンロードボタン
            download_content = f"""稟議書チェック結果
===================
生成日時: {st.session_state.last_result['timestamp']}
使用モデル: {selected_model}
チェックタイプ: 詳細チェック
入力方法: {input_method}
文字数: {len(ringi_text)}文字
評価点数: {st.session_state.last_result.get('score', 'N/A')}/100点
承認可否: {st.session_state.last_result.get('approval', 'N/A')}

{result}

===================
※このチェック結果はAIによる分析であり、最終的な判断は人間が行ってください。
"""
            st.download_button(
                label="📥 チェック結果をダウンロード",
                data=download_content,
                file_name=f"ringi_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        else:
            st.error("チェック結果を取得できませんでした。")
    
    elif not ringi_text.strip():
        st.info("👆 上記に稟議書をアップロードまたは入力してください")
        st.markdown("""
        ### 📋 使用方法
        
        **PDFアップロード**:
        1. 「PDFアップロード」を選択
        2. 稟議書のPDFファイルをアップロード
        3. 自動でテキストが抽出されます
        4. 必要に応じてテキストを編集
        
        **テキスト入力**:
        1. 「テキスト入力」を選択
        2. 稟議書の内容を直接入力
        3. またはサンプル稟議書を読み込み
        
        **対応PDFファイル**:
        - テキストベースのPDF
        - スキャンされた画像PDFは非対応
        - ファイルサイズ: 200MB以下推奨
        """)
    
    # 過去の結果表示
    if 'last_result' in st.session_state:
        st.markdown("---")
        with st.expander("📜 前回のチェック結果"):
            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"生成日時: {st.session_state.last_result['timestamp']}")
                st.caption(f"使用モデル: {st.session_state.last_result['model']}")
                st.caption(f"入力方法: {st.session_state.last_result.get('input_method', 'テキスト入力')}")
            with col2:
                st.caption(f"文字数: {st.session_state.last_result.get('char_count', 'N/A')}文字")
                st.caption(f"評価点数: {st.session_state.last_result.get('score', 'N/A')}/100点")
                st.caption(f"承認可否: {st.session_state.last_result.get('approval', 'N/A')}")
            
            st.markdown(st.session_state.last_result['text'])
    
    # フッター
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_items = sum(len(items) for items in check_items.values())
        st.metric("📋 チェック項目", f"{total_items}項目")
    
    with col2:
        st.metric("🤖 利用可能モデル", f"{len(MODELS)}種類")
    
    with col3:
        if 'last_result' in st.session_state:
            st.metric("⏰ 最終チェック", st.session_state.last_result['timestamp'].split()[1])
    
    st.markdown(
        """
        <div style='text-align: center; color: gray; margin-top: 20px;'>
            Powered by Amazon Bedrock | Claude & Nova Models
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    # App Runner 用のポート設定
    port = int(os.environ.get("PORT", 8080))
    main()
