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

    // Continuous update
    setInterval(addActivity, 4000);

    // Legacy Support Check
    if (!window.CSS || !CSS.supports || !CSS.supports('display', 'flex')) {
        const warning = document.getElementById('legacy-warning');
        if (warning) warning.style.display = 'block';
        document.body.classList.add('is-legacy');
    }
});
