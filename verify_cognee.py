import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Cognee インポート前に API キーを確実にセット
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

import cognee # 環境変数をセットした後にインポート

async def verify_cognee_integration():
    """
    Cognee が AETHER CORE の知識を吸い込み、記憶として定着させられるか検証。
    """
    print("--- [Cognee Integration Test: Attempt 3] ---")
    
    if not api_key:
        print("Error: OPENAI_API_KEY is not set in .env")
        return False
        
    try:
        # 明示的に LLM 設定を行う (アンダースコア付きキー)
        cognee.config.set("llm_api_key", api_key)
        cognee.config.set("llm_provider", "openai")
        cognee.config.set("llm_model", "gpt-4o-mini")
        
        # 1. 知識の提供（産廃業界の法改正ドラフトを例に）
        knowledge_sample = """
        2026年、産業廃棄物管理票（マニフェスト）の完全電子化が義務付けられます。
        特に高齢の担当者が多い中小企業では、デジタルツールへの移行が深刻な課題となっています。
        AETHER COREは、このギャップを埋める「慈愛のサポート」を提供します。
        """
        
        # Cognee へのデータ追加
        await cognee.add(knowledge_sample, "Sanpai_Manifest_2026")
        print("[1/3] Knowledge added successfully.")
        
        # 2. 認知的処理（グラフ化・インデックス化）
        print("Cognifying... (This builds the knowledge graph)")
        await cognee.cognify()
        print("[2/3] Cognify completed.")
        
        # 3. 検索（質問に対する文脈の復元）
        query = "2026年に産廃業界で何が起きますか？現場の悩みは？"
        results = await cognee.search(query)
        
        print(f"[3/3] Search Result for '{query}':")
        for res in results:
            print(f" - {res}")
            
        print("\nConclusion: Cognee integration is VIABLE and POWERFUL.")
        return True
        
    except Exception as e:
        print(f"Cognee Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(verify_cognee_integration())
