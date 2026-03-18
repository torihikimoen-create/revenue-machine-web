import asyncio
import os
import cognee
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class AetherKnowledgeEngine:
    """
    AETHER CORE の『深層知能』を担当するクラス。
    Cognee を使用してナレッジグラフを構築し、スキルの管理と知識の検索を行う。
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            os.environ["OPENAI_API_KEY"] = self.api_key
        
        # Cognee の初期設定
        cognee.config.set("llm_api_key", self.api_key)
        cognee.config.set("llm_provider", "openai")
        cognee.config.set("llm_model", "gpt-4o-mini") # コストと速度のバランス

    async def add_knowledge(self, data: str, dataset_name: str):
        """知識を追加する"""
        await cognee.add(data, dataset_name)
        print(f"Added knowledge to dataset: {dataset_name}")

    async def build_graph(self):
        """ナレッジグラフを構築（Cognify）する"""
        print("Building knowledge graph... This may take a while.")
        await cognee.cognify()
        print("Graph construction completed.")

    async def search_context(self, query: str):
        """文脈を汲み取った検索を行う"""
        results = await cognee.search(query)
        return results

    async def register_skills(self, skills_dir: str = "skills"):
        """SKILL.md 形式のスキルを Cognee にインデックス化する（将来的な拡張用）"""
        skills_path = Path(skills_dir)
        if not skills_path.exists():
            return
            
        for skill_file in skills_path.glob("**/SKILL.md"):
            with open(skill_file, "r", encoding="utf-8") as f:
                skill_content = f.read()
                await self.add_knowledge(skill_content, f"Skill_{skill_file.parent.name}")

async def main():
    # 統合テスト
    engine = AetherKnowledgeEngine()
    
    # スキルの登録
    await engine.register_skills()
    
    # 業界知識のインジェスト（例としてガイドラインを読み込む）
    guideline_path = "../../brain/031647d8-d29f-461f-ae0b-f52321b83fa3/BENEVOLENT_BUSINESS_GUIDELINE.md"
    if os.path.exists(guideline_path):
        with open(guideline_path, "r", encoding="utf-8") as f:
            await engine.add_knowledge(f.read(), "Core_Guideline")
    
    # グラフ構築（初回実行時は時間がかかるため注意）
    # await engine.build_graph() 
    
    print("Aether Knowledge Engine initialized with skills and guidelines.")

if __name__ == "__main__":
    asyncio.run(main())
