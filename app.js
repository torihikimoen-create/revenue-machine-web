// 収益データのカウントアップアニメーション
function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        obj.innerHTML = "¥" + value.toLocaleString();
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

document.addEventListener('DOMContentLoaded', () => {
    const revenueElement = document.getElementById('stat-revenue');
    // ダミーの開始値から目標値までカウントアップ
    animateValue(revenueElement, 1100000, 1240500, 2000);

    // Live Activity Feed Logic
    const feed = document.getElementById('activity-feed');
    const activities = [
        { text: "AI Hunter: Tokyo - Detected osteopathy clinic with review gap.", city: "Tokyo" },
        { text: "AI Hunter: NY - Found luxury salon requiring 24/7 support.", city: "NY" },
        { text: "AI Builder: Generating custom proposal for London law firm.", city: "London" },
        { text: "SNS Sniper: Personalized DM sent to @famous_creator (JP).", city: "Tokyo" },
        { text: "B2B Finder: High-value deal identified: 'Server Data Cleanup'.", city: "Global" },
        { text: "AI Analysis: Competitor review patterns matched in 3 cities.", city: "Global" },
        { text: "SNS Sniper: Bilingual response generated for NY client inquiry.", city: "NY" },
        { text: "System: Auto-balancing worker nodes for optimal throughput.", city: "System" }
    ];

    function addActivity() {
        const activity = activities[Math.floor(Math.random() * activities.length)];
        const item = document.createElement('div');
        item.className = 'activity-item';
        
        const now = new Date();
        const timeStr = now.getHours().toString().padStart(2, '0') + ":" + 
                        now.getMinutes().toString().padStart(2, '0') + ":" + 
                        now.getSeconds().toString().padStart(2, '0');

        item.innerHTML = `
            <span><span style="color:var(--primary)">[${activity.city}]</span> ${activity.text}</span>
            <span class="time">${timeStr}</span>
        `;

        feed.insertBefore(item, feed.firstChild);

        if (feed.children.length > 4) {
            feed.lastChild.style.animation = 'fadeOut 0.5s ease-out forwards';
            setTimeout(() => {
                if (feed.lastChild) feed.removeChild(feed.lastChild);
            }, 500);
        }
    }

    // Initial fill
    for(let i=0; i<3; i++) {
        setTimeout(addActivity, i * 1000);
    }

    // Quick Feedback Logic
    const fbButtons = document.querySelectorAll('.fb-btn');
    fbButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.id;
            const emoji = btn.innerText;
            
            // シンプルなトースト通知の作成
            const toast = document.createElement('div');
            toast.className = 'feedback-toast';
            toast.style.cssText = `
                position: fixed;
                bottom: 30px;
                left: 50%;
                transform: translateX(-50%) translateY(20px);
                background: rgba(0, 242, 255, 0.2);
                border: 1px solid var(--primary);
                backdrop-filter: blur(10px);
                color: white;
                padding: 10px 25px;
                border-radius: 50px;
                font-size: 0.9rem;
                z-index: 1000;
                opacity: 0;
                transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            `;
            
            let msg = "フィードバックありがとうございます！";
            if (type === 'fb-up') msg = "🎉 応援ありがとうございます！励みになります。";
            if (type === 'fb-down') msg = "📝 改善のご指摘ありがとうございます。即座に調整します。";
            if (type === 'fb-idea') msg = "💡 素晴らしいアイデアをありがとうございます！";
            
            toast.innerText = msg;
            document.body.appendChild(toast);
            
            // アニメーション表示
            setTimeout(() => {
                toast.style.opacity = '1';
                toast.style.transform = 'translateX(-50%) translateY(0)';
            }, 100);
            
            // 消去
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(-50%) translateY(-20px)';
                setTimeout(() => document.body.removeChild(toast), 500);
            }, 3000);
            
            // ログ出力（将来的にサーバーへ送信）
            console.log(`[Feedback] Type: ${type}, Emoji: ${emoji}`);
        });
    });


    // AI Ad Auditor Logic (MVP Demo)
    const adInput = document.getElementById('ad-input');
    const diagnoseBtn = document.getElementById('diagnose-btn');
    const adResult = document.getElementById('ad-result');

    diagnoseBtn.addEventListener('click', () => {
        const text = adInput.value.trim();
        if (!text) {
            alert("広告コピーを入力してください。");
            return;
        }

        // ローディング表示
        adResult.innerHTML = `
            <div class="loading-spinner"></div>
            <p style="text-align:center; color:var(--primary);">AIが法的リスクを分析中...</p>
        `;
        diagnoseBtn.disabled = true;

        // シミュレーション（実際にはサーバーサイドの AdComplianceEngine を叩くことを想定）
        setTimeout(() => {
            const riskyKeywords = ["絶対", "痩せ", "病気", "治る", "若返る", "魔法", "シワ", "消え"];
            const foundIssues = riskyKeywords.filter(kw => text.includes(kw));

            if (foundIssues.length > 0) {
                // RISKY の場合
                let issuesHtml = foundIssues.map(kw => `
                    <div class="issue-item">
                        <span class="law">[薬機法/景表法]</span>
                        <span>表現「${kw}」に不当な暗示または誇大表現のリスクがあります。</span>
                    </div>
                `).join('');

                // 修正案のシミュレーション（Humanizer.polishの結果を想定）
                let polished = text;
                if (text.includes("痩せ") || text.includes("絶対")) {
                    polished = "理想のスタイルを目指す、毎日の健康習慣に。あなたの輝きをサポートします。";
                } else if (text.includes("若返る") || text.includes("シワ")) {
                    polished = "肌にうるおいを与え、ハリのある毎日を。年齢に応じたケアで自分らしい美しさを。";
                } else {
                    polished = "毎日のコンディションを整え、穏やかな時間を提供します。";
                }

                adResult.innerHTML = `
                    <div class="result-header">
                        <span style="font-weight:700;">分析結果</span>
                        <span class="status-badge risky">Risky / 要修正</span>
                    </div>
                    <div class="issue-list">${issuesHtml}</div>
                    <div class="polished-box">
                        <h5>AI安全リライト案</h5>
                        <div class="polished-text">${polished}</div>
                    </div>
                `;
            } else {
                // SAFE の場合
                adResult.innerHTML = `
                    <div class="result-header">
                        <span style="font-weight:700;">分析結果</span>
                        <span class="status-badge safe">Clean / 安全</span>
                    </div>
                    <p style="font-size:0.9rem; color:rgba(255,255,255,0.7);">法的リスクは見つかりませんでした。このコピーは安全に使用できる可能性が高いです。</p>
                    <div class="polished-box" style="background:rgba(0, 224, 142, 0.1); border-color:#00e08e;">
                        <h5>ステータス</h5>
                        <div class="polished-text">そのまま使用可能です。</div>
                    </div>
                `;
            }
            diagnoseBtn.disabled = false;
        }, 1800);
    });

    // Continuous update
    setInterval(addActivity, 4000);

    // Legacy Support Check
    if (!window.CSS || !CSS.supports || !CSS.supports('display', 'flex')) {
        const warning = document.getElementById('legacy-warning');
        if (warning) warning.style.display = 'block';
        document.body.classList.add('is-legacy');
    }
});
