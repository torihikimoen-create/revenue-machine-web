# 🏁 ゴールへの最終ロードマップ：不労所得のスイッチを入れる

これまでの開発で「最強のAI兵隊」は完成しました。あとは、彼らに「武器（API）」と「戦場（クラウド）」を与え、号令をかけるだけです。

## STEP 1: 「燃料」の準備（OpenAI API）
あなたの分身となるAIを動かすための設定です。
1.  [OpenAI Platform](https://platform.openai.com/signup) でアカウント作成。
2.  [Billing](https://platform.openai.com/account/billing) から5ドル程度をチャージ。
3.  [API Keys](https://platform.openai.com/account/api-keys) で「sk-...」という鍵をコピー。
4.  [Usage limits](https://platform.openai.com/account/billing/limits) で予算制限（例：月10ドル）を設定。

## STEP 2: 「戦場」の確保（GitHub）
あなたのPCがオフでもAIが働く場所を作ります。
1.  [GitHub](https://github.com/) アカウントを作成（無料）。
2.  今回のプロジェクト一式を「新規リポジトリ」としてアップロード（Push）。
3.  リポジトリの **Settings > Secrets** に、STEP 1で取得した「sk-...」を登録。

## STEP 3: 「爆撃」の開始（Live Fire）
いよいよ本番です。
1.  GitHub上の **Actions** タブを開く。
2.  `24/7 Auto-Business Engine` というワークフローを選択。
3.  **Run workflow** ボタンを押し、最初のアプローチを手動で実行してみる。
4.  以降は、設定した時間に勝手にAIが目覚め、営業活動を代行します。

---

> [!TIP]
> **オーナーとしての仕事**
> これからのあなたの仕事は、「どこを攻めるか（クリニックのエリア、SNSのジャンルなど）」をターゲットリストに追加するだけです。
> 1ヶ月後、Stripeに積み上がった「利確」された報酬を確認するのを楽しみにしてください。
