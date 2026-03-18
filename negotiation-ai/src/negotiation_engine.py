import logging

class NegotiationAI:
    """
    商談・クロージングを自動化するAI。
    相手の返信トーンを解析し、最適な追撃や決済誘導を行う。
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_response(self, response_text: str):
        """
        相手の返信内容からインテント（意図）を判定する。
        """
        response_text = response_text.lower()
        
        if any(kw in response_text for kw in ["興味", "詳細", "話を聞きたい", "詳しく", "interested", "details"]):
            return "INTERESTED"
        elif any(kw in response_text for kw in ["いくら", "料金", "費用", "価格", "price", "cost"]):
            return "PRICING"
        elif any(kw in response_text for kw in ["怪しい", "本当か", "難しい", "できない", "skeptical", "hard"]):
            return "SKEPTICAL"
        else:
            return "GENERIC"

    def generate_next_step(self, intent: str, clinic_name: str):
        """
        判定された意図に基づき、次のアクション（返信文とリンク）を生成する。
        """
        actions = {
            "INTERESTED": {
                "message": f"【{clinic_name}様】ご興味をお持ちいただきありがとうございます！貴院の過去の口コミを解析した『返信サンプル』を作成しました。以下よりご確認いただき、問題なければそのまま自動化を開始いただけます。",
                "link": "https://buy.stripe.com/test_interested_demo", # 仮のStripeリンク
                "button": "デモを確認して開始する"
            },
            "PRICING": {
                "message": f"【{clinic_name}様】料金プランについてのご質問ありがとうございます。本システムは月額3万円（税別）のワンプランで、初期費用は一切かかりません。口コミ返信1件あたりのコストを数円に抑え、先生の時給換算で月間数十万円のコスト削減を実現します。",
                "link": "https://buy.stripe.com/test_pricing_plan",
                "button": "プランに申し込む"
            },
            "SKEPTICAL": {
                "message": f"【{clinic_name}様】ご懸念、ごもっともです。AIが作成する文章の質に不安を感じられるのは当然かと存じます。まずは『貴院専用の無料デモ』で、AIがどれほど自然な文章を生成するか、一度お手元のデータでお試しになりませんか？",
                "link": "https://calendly.com/demo-reservation", # 仮の予約リンク
                "button": "無料デモを予約する"
            },
            "GENERIC": {
                "message": f"【{clinic_name}様】お問い合わせありがとうございます。貴院の口コミ管理を自動化し、地域No.1の信頼を築くお手伝いをさせていただければ幸いです。まずは詳細資料を以下よりご覧ください。",
                "link": "https://example.com/automation-guide",
                "button": "資料をダウンロードする"
            }
        }
        return actions.get(intent, actions["GENERIC"])

if __name__ == "__main__":
    # シミュレーション実行
    ai = NegotiationAI()
    test_cases = [
        {"name": "銀座矯正歯科", "msg": "非常に興味があります。具体的な進め方を教えてください。"},
        {"name": "ブランパ銀座", "msg": "導入費用はいくらですか？"},
        {"name": "渋谷矯正歯科", "msg": "AIに任せるのは少し不安です。"},
    ]
    
    for case in test_cases:
        intent = ai.analyze_response(case["msg"])
        action = ai.generate_next_step(intent, case["name"])
        print(f"\n--- 商談シミュレーション: {case['name']} ---")
        print(f"相手の返信: {case['msg']}")
        print(f"AI判定意図: {intent}")
        print(f"AI追撃文: {action['message']}")
        print(f"提示リンク: {action['link']}")
        print(f"アクションボタン: {action['button']}")
