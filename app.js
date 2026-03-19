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

    // Modal Logic
    const signupModal = document.getElementById('signup-modal');
    const trialTriggers = document.querySelectorAll('.trial-trigger');
    const closeModal = document.getElementById('close-modal');
    const signupForm = document.getElementById('signup-form');

    trialTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            if (trigger.getAttribute('href') === '#') {
                e.preventDefault();
                signupModal.classList.add('active');
            }
        });
    });

    closeModal.addEventListener('click', () => {
        signupModal.classList.remove('active');
    });

    window.addEventListener('click', (e) => {
        if (e.target === signupModal) {
            signupModal.classList.remove('active');
        }
    });

    signupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const userName = document.getElementById('user-name').value;
        const submitBtn = signupForm.querySelector('button[type="submit"]');
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<div class="loading-spinner" style="width:20px; height:20px; border-width:2px; margin:0 auto;"></div>';

        // 登録完了のシミュレーション
        setTimeout(() => {
            // 3秒後にダッシュボードへ遷移する体にする
            setTimeout(() => {
                // ダッシュボードUIの生成
                document.body.innerHTML = `
                    <div class="background-blur"></div>
                    <header>
                        <nav>
                            <div class="logo"><a href="index.html" class="logo-text">AETHER <span>CORE</span></a></div>
                            <div class="user-profile">
                                <span>${userName} 様</span>
                                <div class="avatar">👤</div>
                            </div>
                        </nav>
                    </header>
                    <main class="dashboard-main">
                        <aside class="sidebar glass">
                            <ul>
                                <li class="active">📊 概要</li>
                                <li>📤 分析・送信</li>
                                <li>🤖 監査エンジン</li>
                                <li>📂 ナレッジベース</li>
                                <li>⚙️ 設定</li>
                            </ul>
                        </aside>
                        <section class="dashboard-content">
                            <div class="welcome-header">
                                <h1>おかえりなさい、${userName}様</h1>
                                <p>システムは正常に稼働しており、${new Date().toLocaleDateString()} の分析を開始しました。</p>
                            </div>
                            <div class="stats-grid">
                                <div class="stat-card glass">
                                    <span class="label">本日の監査件数</span>
                                    <span class="value">128</span>
                                </div>
                                <div class="stat-card glass">
                                    <span class="label">自動送信済み</span>
                                    <span class="value">42</span>
                                </div>
                                <div class="stat-card glass">
                                    <span class="label">AI稼働効率</span>
                                    <span class="value">98.5%</span>
                                </div>
                            </div>
                            <div class="recent-activity glass">
                                <h3>最近の自動処理</h3>
                                <div class="activity-list">
                                    <div class="activity-row"><span>・Googleマップ レビュー返信予約済み (3件)</span> <span class="time">10分前</span></div>
                                    <div class="activity-row"><span>・中建審 労務費データ同期完了</span> <span class="time">25分前</span></div>
                                    <div class="activity-row"><span>・提出用レポートの下書き作成完了</span> <span class="time">1時間前</span></div>
                                </div>
                            </div>
                        </section>
                    </main>
                    <style>
                        .dashboard-main { display: flex; gap: 2rem; padding: 100px 5% 50px; min-height: 100vh; }
                        .sidebar { width: 250px; padding: 2rem; height: fit-content; }
                        .sidebar ul { list-style: none; }
                        .sidebar li { padding: 12px 15px; margin-bottom: 5px; border-radius: 8px; cursor: pointer; transition: 0.3s; }
                        .sidebar li.active { background: var(--primary); color: var(--bg); font-weight: 700; }
                        .sidebar li:hover:not(.active) { background: rgba(255,255,255,0.1); }
                        .dashboard-content { flex: 1; }
                        .welcome-header { margin-bottom: 2rem; }
                        .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2rem; }
                        .stat-card { text-align: center; padding: 1.5rem !important; }
                        .stat-card .label { display: block; font-size: 0.8rem; opacity: 0.6; margin-bottom: 0.5rem; }
                        .stat-card .value { font-size: 2rem; font-weight: 700; color: var(--primary); }
                        .recent-activity { padding: 2rem !important; }
                        .activity-list { margin-top: 1.5rem; }
                        .activity-row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.9rem; }
                        .user-profile { display: flex; align-items: center; gap: 10px; }
                        .avatar { font-size: 1.5rem; }
                    </style>
                `;
                window.scrollTo(0,0);

                // タブ切り替えロジックの追加
                const attachDashboardListeners = () => {
                    const contentArea = document.querySelector('.dashboard-content');
                    const sidebarItems = document.querySelectorAll('.sidebar li');
                    
                    const setupDashboardBehaviors = (viewName) => {
                        // AI分析ボタンのセットアップ
                        const dashDiagnoseBtn = document.getElementById('dash-diagnose-btn');
                        const dashAdInput = document.getElementById('dash-ad-input');
                        const adResult = document.getElementById('dash-ad-result');

                        if (dashDiagnoseBtn && dashAdInput) {
                            dashDiagnoseBtn.addEventListener('click', () => {
                                const text = dashAdInput.value.trim();
                                if (!text) return;
                                adResult.innerHTML = `<div class="loading-spinner" style="width:30px; height:30px;"></div><p style="text-align:center;">AI分析中...</p>`;
                                dashDiagnoseBtn.disabled = true;
                                setTimeout(() => {
                                    const risky = ["絶対", "痩せ", "病気", "治わる", "魔法"];
                                    const found = risky.filter(kw => text.includes(kw));
                                    if (found.length > 0) {
                                        adResult.innerHTML = `<div class="status-badge risky">⚠️ リスクあり</div><div class="polished-box"><h5>✨ リライト案</h5><p>${text.replace(/絶対|痩せ|魔法/g, "適正な")}...（AI調整済み）</p></div>`;
                                    } else {
                                        adResult.innerHTML = `<div class="status-badge safe">✅ 安全確認</div><p>法令遵守されています。</p>`;
                                    }
                                    dashDiagnoseBtn.disabled = false;
                                }, 1500);
                            });

                            // ドラッグ＆ドロップのセットアップ
                            dashAdInput.addEventListener('dragover', (e) => {
                                e.preventDefault();
                                dashAdInput.style.borderColor = 'var(--primary)';
                                dashAdInput.style.background = 'rgba(0, 242, 255, 0.05)';
                            });
                            dashAdInput.addEventListener('dragleave', () => {
                                dashAdInput.style.borderColor = 'rgba(255,255,255,0.1)';
                                dashAdInput.style.background = 'rgba(0,0,0,0.2)';
                            });
                            dashAdInput.addEventListener('drop', (e) => {
                                e.preventDefault();
                                dashAdInput.style.borderColor = 'rgba(255,255,255,0.1)';
                                dashAdInput.style.background = 'rgba(0,0,0,0.2)';
                                const file = e.dataTransfer.files[0];
                                if (file) {
                                    const reader = new FileReader();
                                    reader.onload = (ev) => { dashAdInput.value = ev.target.result; };
                                    reader.readAsText(file);
                                } else {
                                    dashAdInput.value = e.dataTransfer.getData('text');
                                }
                            });
                        }
                    };

                    const views = {
                        '概要': `
                            <div class="welcome-header">
                                <h1>おかえりなさい、${userName}様</h1>
                                <p>システムは正常に稼働しており、${new Date().toLocaleDateString()} の分析を開始しました。</p>
                            </div>
                            <div class="stats-grid">
                                <div class="stat-card glass"><span class="label">監査件数</span><span class="value">128</span></div>
                                <div class="stat-card glass"><span class="label">自動送信済み</span><span class="value">42</span></div>
                                <div class="stat-card glass"><span class="label">AI稼働効率</span><span class="value">98.5%</span></div>
                            </div>
                            <div class="recent-activity glass">
                                <h3>最近の自動処理</h3>
                                <div class="activity-list">
                                    <div class="activity-row"><span>・Googleマップ 返信済み</span> <span class="time">10分前</span></div>
                                    <div class="activity-row"><span>・中建審 データ同期完了</span> <span class="time">25分前</span></div>
                                </div>
                            </div>
                        `,
                        '分析・送信': `
                            <div class="welcome-header">
                                <h1>📤 分析・送信（Analyse & Send）</h1>
                                <p>AIが分析し、最適な内容で自動送信・提案を行うセクションです。</p>
                            </div>
                            <div class="glass" style="margin-bottom:2rem; padding:2rem !important;">
                                <h3 style="margin-bottom:1rem; color:var(--primary);">✨ AI分析・下書き生成</h3>
                                <p style="font-size:0.8rem; margin-bottom:1rem; opacity:0.7;">広告コピーの入力や、ファイルをここにドロップしてください。</p>
                                <textarea id="dash-ad-input" placeholder="ここにテキストを入力するか、ファイルをドロップ（.txt/.md）"></textarea>
                                <button id="dash-diagnose-btn" class="btn primary" style="width:100%; margin-top:1rem;">分析を実行</button>
                                <div id="dash-ad-result" style="margin-top:1.5rem;"></div>
                            </div>
                            <div class="recent-activity glass">
                                <h3>履歴</h3>
                                <div class="activity-list">
                                    <div class="activity-row"><span>📩 B2B提案送信済み</span> <span class="time">30分前</span></div>
                                </div>
                            </div>
                        `,
                        '監査エンジン': `
                            <div class="welcome-header"><h1>🤖 監査エンジン</h1><p>AIエージェントの稼働状況です。</p></div>
                            <p class="glass" style="padding:2rem !important;">建設業法 遵守監査: <span style="color:#00ff88">稼働中</span></p>
                        `,
                        'ナレッジベース': `
                            <div class="welcome-header"><h1>📂 ナレッジベース</h1><p>同期済みの法令データです。</p></div>
                            <p class="glass" style="padding:2rem !important;">📄 建設業振興指針 (2026年度版)</p>
                        `,
                        '設定': `
                            <div class="welcome-header"><h1>⚙️ 設定</h1><p>システム構成の管理</p></div>
                            <div class="glass" style="padding:2rem !important;"><p>無料トライアル期間: あと9日</p></div>
                        `
                    };

                    sidebarItems.forEach(item => {
                        item.addEventListener('click', () => {
                            sidebarItems.forEach(i => i.classList.remove('active'));
                            item.classList.add('active');
                            const viewName = item.innerText.replace(/^[^\s]+\s/, '');
                            contentArea.innerHTML = views[viewName] || views['概要'];
                            setupDashboardBehaviors(viewName);
                        });
                    });

                    // 初期状態のセットアップ
                    setupDashboardBehaviors('概要');
                };

                attachDashboardListeners();
            }, 2500);
        }, 1500);
    });

    // Continuous update (Safety check added for dashboard view)
    setInterval(() => {
        const activityList = document.querySelector('.activity-list');
        if (!activityList) return; // Dashboard or different view might not have this specific list
        
        // Original addActivity logic if needed, or skip if in dashboard
        if (typeof addActivity === 'function' && !document.querySelector('.dashboard-main')) {
            addActivity();
        }
    }, 4000);
});
