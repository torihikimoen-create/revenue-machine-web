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

    // 将来的にはここでGitHub Pages上のJSONデータをフェッチし、
    // エンジンの最新稼働状況を反映させる
    /*
    fetch('status.json')
        .then(response => response.json())
        .then(data => {
            // UIを更新
        });
    */
});
