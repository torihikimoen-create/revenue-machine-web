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
                        const dashDiagnoseBtn = document.getElementById('dash-diagnose-btn');
                        const dashAdInput = document.getElementById('dash-ad-input');
                        const adResult = document.getElementById('dash-ad-result');

                        if (dashDiagnoseBtn && dashAdInput) {
                            const performAnalysis = (text) => {
                                adResult.innerHTML = `<div class="loading-spinner" style="width:30px; height:30px;"></div><p style="text-align:center;">AIコンテクスト解析中...</p>`;
                                dashDiagnoseBtn.disabled = true;

                                setTimeout(() => {
                                    const isManifest = /manifest|マニフェスト|EPA|F003|solvent|sludge|産業廃棄物/i.test(text);
                                    const isAdCopy = /絶対|痩せ|魔法|治る|若返る|シワ/i.test(text);
                                    const isFutureDate = /2027|2028|2029|2030/.test(text);

                                    if (isFutureDate) {
                                        adResult.innerHTML = `
                                            <div style="font-size:0.75rem; color:var(--primary); margin-bottom:5px; font-weight:700;">担当部署: 産業廃棄物・資源監査室 × ガバナンス部</div>
                                            <div class="status-badge risky" style="background:#ff4757;">❌ 判定: 受理不可 (不実記載リスク)</div>
                                            <div class="polished-box" style="border-left: 4px solid #ff4757;">
                                                <h5 style="color:#ff4757; margin-bottom:8px;">⚠️ 交付年月日の一部不整合</h5>
                                                <p style="font-size:0.85rem; line-height:1.4;">
                                                    日付が <strong>「2027年」</strong> となっており、現在時刻との整合性が取れません。廃棄物処理法に基づくマニフェスト交付義務（同時交付）に違反し、虚偽記載と判断されるリスクが極めて高いです。
                                                </p>
                                                <div style="margin-top:10px; padding:10px; background:rgba(255,255,255,0.05); font-size:0.8rem;">
                                                    <strong>アクション:</strong> 正しい日付での再交付を指示してください。
                                                </div>
                                            </div>
                                        `;
                                    } else if (isManifest) {
                                        adResult.innerHTML = `
                                            <div style="font-size:0.75rem; color:var(--primary); margin-bottom:5px; font-weight:700;">担当部署: 産業廃棄物・資源監査室</div>
                                            <div class="status-badge risky" style="background:#ff4757;">⚠️ 監査アラート: 内容不備</div>
                                            <div class="polished-box" style="border-left: 4px solid #ff4757;">
                                                <h5 style="color:#ff4757; margin-bottom:8px;">📌 検出された不備</h5>
                                                <p style="font-size:0.85rem; line-height:1.4;">許可品目「引火性廃油」の含有が疑われますが、委託先施設の許可範囲外である可能性があります。詳細な照合が必要です。</p>
                                            </div>
                                        `;
                                    } else if (isAdCopy) {
                                        const risky = ["絶対", "痩せ", "魔法", "治る", "若返る", "シワ"];
                                        adResult.innerHTML = `
                                            <div style="font-size:0.75rem; color:var(--primary); margin-bottom:5px; font-weight:700;">担当部署: 広告・PR法務室</div>
                                            <div class="status-badge risky">⚠️ 薬機法・景表法リスクを検知</div>
                                            <div class="polished-box">
                                                <h5 style="color:var(--primary); margin-bottom:8px;">✨ AI安全リライト提案</h5>
                                                <div class="polished-text" style="font-size:0.9rem;">${text.replace(/絶対|痩せ|魔法|治る|若返る|シワ/g, "理想の成果を追求する")}... (専門部署による調整済み)</div>
                                            </div>
                                        `;
                                    } else {
                                        adResult.innerHTML = `<div class="status-badge safe">✅ 安全 (Clear)</div><p style="font-size:0.9rem;">重大な法的リスクは検出されませんでした。</p>`;
                                    }
                                    dashDiagnoseBtn.disabled = false;
                                }, 1800);
                            };

                            dashDiagnoseBtn.addEventListener('click', () => {
                                performAnalysis(dashAdInput.value.trim());
                            });

                            dashAdInput.addEventListener('dragover', (e) => {
                                e.preventDefault();
                                dashAdInput.style.borderColor = 'var(--primary)';
                            });
                            dashAdInput.addEventListener('dragleave', () => {
                                dashAdInput.style.borderColor = 'rgba(255,255,255,0.1)';
                            });
                            dashAdInput.addEventListener('drop', (e) => {
                                e.preventDefault();
                                const file = e.dataTransfer.files[0];
                                if (!file) return;

                                if (file.type.startsWith('image/')) {
                                    adResult.innerHTML = `<div class="loading-spinner"></div><p style="text-align:center;">視覚監査・法的整合性チェックを同時実行中...</p>`;
                                    setTimeout(() => {
                                        // ユーザーが提示した画像（2027年マニフェスト）のシミュレーション
                                        const mockManifestText = "産業廃棄物管理票(直行用) [A票], 交付年月日: 2027年10月1日, 排出事業者: 株式会社光和テック, 捺印: 良好";
                                        
                                        // ここでも未来日を検知する論理を追加
                                        const isFuture = mockManifestText.includes("2027");
                                        
                                        dashAdInput.value = mockManifestText;
                                        
                                        adResult.innerHTML = `
                                            <div style="font-size:0.75rem; color:var(--primary); font-weight:700;">担当: 産業廃棄物・資源監査室 × 視覚的完全性監査室</div>
                                            <div class="status-badge risky" style="background:#ff4757;">❌ 総合判定: 受理不可 (日付の不実記載)</div>
                                            <div class="polished-box" style="border-left: 4px solid #ff4757;">
                                                <h5 style="color:#ff4757; margin-bottom:8px;">⚖️ 専門官の最終判決</h5>
                                                <p style="font-size:0.85rem; line-height:1.4;">
                                                    <strong>視覚監査結果:</strong> 紙面状態および捺印は「極めて良好」です。偽造の形跡もありません。<br>
                                                    <strong>法的監査結果:</strong> 致命的な矛盾を検知。交付日が <strong>2027年</strong> となっており、現時点での交付は不可能です。形式が完璧であっても、内容に不実があれば書類は無効となります。
                                                </p>
                                                <div style="margin-top:10px; font-size:0.75rem; opacity:0.8;">
                                                    ※専門部署の「目」をダッシュボードへ完全同期しました。
                                                </div>
                                            </div>
                                        `;
                                        dashDiagnoseBtn.disabled = false;
                                    }, 2000);
                                } else {
                                    const reader = new FileReader();
                                    reader.onload = (ev) => {
                                        dashAdInput.value = ev.target.result;
                                        performAnalysis(ev.target.result);
                                    };
                                    reader.readAsText(file);
                                }
                            });
                        }

                        // 監査エンジンのインタラクティブ化
                        const auditCards = document.querySelectorAll('.audit-card');
                        const auditDetail = document.getElementById('audit-detail-area');
                        if (auditCards.length > 0 && auditDetail) {
                            auditCards.forEach(card => {
                                card.addEventListener('click', () => {
                                    const typeName = card.querySelector('h4').innerText;
                                    auditDetail.innerHTML = `
                                        <div class="glass" style="padding:2rem; animation: slideIn 0.3s ease-out; margin-top:2rem;">
                                            <h3 style="color:var(--primary); margin-bottom:1rem;">📊 監査詳細レポート: ${typeName}</h3>
                                            <div class="polished-box" style="background:rgba(255,255,255,0.03);">
                                                <p style="font-size:0.85rem; line-height:1.6;">
                                                    <strong>監査ステータス:</strong> 稼働中 (Active)<br>
                                                    <strong>最終一律監査:</strong> 15分前<br>
                                                    <strong>今回の指摘事項:</strong> 1件の「不適合リスク」を検知しました。
                                                </p>
                                                <button class="btn primary" style="margin-top:1rem; padding:0.5rem 1rem; font-size:0.8rem;">詳細ログをDL</button>
                                            </div>
                                        </div>
                                    `;
                                });
                            });
                        }

                        // ナレッジベースの検索
                        const kbSearch = document.getElementById('kb-search');
                        const kbItems = document.querySelectorAll('.kb-item');
                        if (kbSearch) {
                            kbSearch.addEventListener('input', (e) => {
                                const q = e.target.value.toLowerCase();
                                kbItems.forEach(item => {
                                    item.style.display = item.innerText.toLowerCase().includes(q) ? 'block' : 'none';
                                });
                            });
                        }

                        // パーソナ切り替え
                        const personas = document.querySelectorAll('.persona-card');
                        if (personas.length > 0) {
                            personas.forEach(p => {
                                p.addEventListener('click', () => {
                                    personas.forEach(x => { x.classList.remove('active'); x.style.opacity = '0.5'; x.style.border = 'none'; });
                                    p.classList.add('active'); p.style.opacity = '1'; p.style.border = '1px solid var(--primary)';
                                });
                            });
                        }
                    };

                    const views = {
                        '概要': `
                            <div class="welcome-header"><h1>おかえりなさい、${userName}様</h1><p>システムは正常に稼働しており、${new Date().toLocaleDateString()} の分析を開始しました。</p></div>
                            <div class="stats-grid">
                                <div class="stat-card glass"><span class="label">監査件数</span><span class="value">128</span></div>
                                <div class="stat-card glass"><span class="label">自動送信済み</span><span class="value">42</span></div>
                                <div class="stat-card glass"><span class="label">AI稼働効率</span><span class="value">98.5%</span></div>
                            </div>
                            <div class="recent-activity glass"><h3>最近の自動処理</h3><div class="activity-list"><div class="activity-row"><span>・Googleマップ 返信済み</span> <span class="time">10分前</span></div><div class="activity-row"><span>・中建審 データ同期完了</span> <span class="time">25分前</span></div></div></div>
                        `,
                        '分析・送信': `
                            <div class="welcome-header"><h1>📤 分析・送信</h1><p>AIが分析し、最適な内容で自動送信・提案を行うセクションです。</p></div>
                            <div class="glass" style="padding:2rem !important;">
                                <h3 style="margin-bottom:1rem; color:var(--primary);">✨ AI分析・下書き生成</h3>
                                <textarea id="dash-ad-input" placeholder="ここにテキストを入力するか、ファイルをドロップ" style="width:100%; height:250px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.1); border-radius:12px; color:white; padding:1.5rem;"></textarea>
                                <button id="dash-diagnose-btn" class="btn primary" style="width:100%; margin-top:1.5rem; padding:1.2rem; font-size:1.1rem;">分析を実行</button>
                                <div id="dash-ad-result" style="margin-top:2rem;"></div>
                            </div>
                        `,
                        '監査エンジン': `
                            <div class="welcome-header"><h1>🤖 監査エンジン</h1><p>特定の法令に基づく専門ユニットを動かします。</p></div>
                            <div class="audit-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:1.5rem;">
                                <div class="audit-card glass hover-effect" data-type="construction" style="padding:1.5rem; cursor:pointer;">
                                    <div style="font-size:1.5rem; margin-bottom:0.5rem;">🏗️</div>
                                    <h4 style="margin-bottom:0.5rem;">建設業法 遵守監査</h4>
                                    <p style="font-size:0.8rem; opacity:0.7;">工期、適正見積の監査。</p>
                                </div>
                                <div class="audit-card glass hover-effect" data-type="waste" style="padding:1.5rem; cursor:pointer;">
                                    <div style="font-size:1.5rem; margin-bottom:0.5rem;">♻️</div>
                                    <h4 style="margin-bottom:0.5rem;">産業廃棄物 適合性監査</h4>
                                    <p style="font-size:0.8rem; opacity:0.7;">マニフェスト、処理法の遵守。</p>
                                </div>
                            </div>
                            <div id="audit-detail-area"></div>
                        `,
                        'ナレッジベース': `
                            <div class="welcome-header"><h1>📚 ナレッジベース</h1><p>地域条例や法的ナレッジの検索。</p></div>
                            <div class="glass" style="margin-bottom:2rem;"><input type="text" id="kb-search" placeholder="キーワード検索..." style="width:100%; background:rgba(0,0,0,0.3); border:none; color:white; padding:1rem;"></div>
                            <div class="kb-results active-list">
                                <div class="kb-item glass" style="padding:1rem; margin-bottom:1rem;"><h4>📍 北海道：地域開発補助金基準</h4><p style="font-size:0.8rem;">札幌周辺の環境規制特例について。</p></div>
                                <div class="kb-item glass" style="padding:1rem; margin-bottom:1rem;"><h4>📍 佐賀県：産廃条例 独自解釈</h4><p style="font-size:0.8rem;">県外搬出時の届け出厳格化。</p></div>
                            </div>
                        `,
                        '設定': `
                            <div class="welcome-header"><h1>⚙️ 設定</h1><p>AIアシスタントのパーソナライズ。</p></div>
                            <div class="glass" style="padding:2rem;">
                                <h3 style="margin-bottom:1.5rem;">🤖 AIパーソナ</h3>
                                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:1rem;">
                                    <div class="persona-card glass active" style="padding:1rem; text-align:center; border:1px solid var(--primary);">Vesta</div>
                                    <div class="persona-card glass" style="padding:1rem; text-align:center; opacity:0.5;">Pallas</div>
                                    <div class="persona-card glass" style="padding:1rem; text-align:center; opacity:0.5;">Mercury</div>
                                </div>
                            </div>
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
