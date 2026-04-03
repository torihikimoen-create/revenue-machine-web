/* ── Flower Data ───────────────────────────────────────── */
const FLOWERS = {
    2:  { name: "Cherry Blossom", emoji: "🌸", keywords: "Perfect Harmony",        pct: 95,
          msg: "Like cherry blossoms that bloom together in a single breath of spring — your connection is rare, beautiful, and deeply in sync. The universe aligned specifically to bring you two together." },
    3:  { name: "White Lily",     emoji: "🤍", keywords: "Pure Radiance",           pct: 84,
          msg: "Yours is a love that shines with purity and clear intention. The White Lily speaks of a bond where both souls bring out each other's truest, most luminous light." },
    4:  { name: "Plum Blossom",   emoji: "🌺", keywords: "Resilient Bond",          pct: 78,
          msg: "Like plum blossoms that dare to bloom in winter, your love grows stronger through challenge. What you are building together has roots deep enough to last a lifetime." },
    5:  { name: "Lavender",       emoji: "💜", keywords: "Calm Devotion",           pct: 81,
          msg: "A peaceful, devoted energy surrounds this connection. Lavender speaks of trust that deepens quietly — the kind that never needs to prove itself, because it simply knows." },
    6:  { name: "Peony",          emoji: "🌹", keywords: "Rich Romance",            pct: 90,
          msg: "The Peony is one of the most romantic flowers in existence — and it chose your bond. Abundance, warmth, and deep emotional richness are woven into everything you share." },
    7:  { name: "Snowdrop",       emoji: "🌱", keywords: "Breakthrough Hope",       pct: 73,
          msg: "The Snowdrop is the first flower to push through frozen ground. This connection carries the energy of hope — especially when life feels heavy, you find each other." },
    8:  { name: "Sunflower",      emoji: "🌻", keywords: "Loyal Warmth",            pct: 85,
          msg: "Sunflowers always turn toward the light — and in this bond, you are each other's light. Unwavering loyalty and genuine, radiant warmth define what you share." },
    9:  { name: "Lotus",          emoji: "🪷", keywords: "Spiritual Union",         pct: 97,
          msg: "The Lotus rises from darkness to bloom in perfect beauty. Your connection transcends the ordinary — this is a spiritual bond written long before you were born." },
    10: { name: "Camellia",       emoji: "🌺", keywords: "Enduring Devotion",       pct: 79,
          msg: "The Camellia blooms in quiet dignity — steady, faithful, enduring. Your love doesn't need to announce itself. It simply is, season after season, and that is everything." },
    11: { name: "Iris",           emoji: "🪻", keywords: "Visionary Bond",          pct: 93,
          msg: "The Iris is the flower of vision and deep faith. You two see each other — truly see — in a way most people never experience. This connection has layers beyond measure." },
    12: { name: "Baby's Breath",  emoji: "🤍", keywords: "Everlasting Love",        pct: 88,
          msg: "Baby's Breath carries the meaning of eternal love and innocence. Soft on the surface, unbreakable at its core — this bond was made to outlast every season." },
    13: { name: "Marigold",       emoji: "🌼", keywords: "Passionate Fire",         pct: 76,
          msg: "Marigold burns with passionate, golden warmth. This connection is alive and intense — and it asks both of you to meet it with equal presence and fire." },
    14: { name: "Forget-me-not",  emoji: "💙", keywords: "True Love",               pct: 86,
          msg: "Forget-me-not is the flower of love that is remembered forever. No matter where life takes you, this connection leaves a mark that time cannot erase." },
    15: { name: "Jasmine",        emoji: "🌟", keywords: "Sweet Grace",             pct: 83,
          msg: "Jasmine is subtle, intoxicating, and unforgettable. Your connection carries a natural grace — it draws people closer without trying, and grows more beautiful with every season." },
    16: { name: "Violet",         emoji: "💜", keywords: "Faithful Heart",          pct: 80,
          msg: "The Violet is the flower of faithful, enduring love. Quiet strength. Loyal hearts. A bond that doesn't waver — even when everything around you shifts." },
    17: { name: "Cosmos",         emoji: "🌸", keywords: "Beautiful Difference",    pct: 77,
          msg: "Cosmos flowers thrive in open, wild places — different from everything around them, yet perfectly in bloom. Your differences are not obstacles. They are your greatest strength." },
    18: { name: "Orchid",         emoji: "🌺", keywords: "Once in a Lifetime",      pct: 99,
          msg: "The Orchid is the rarest flower in the world — and so is this bond. Once in a lifetime, the universe creates something like this. You found each other. That is the sign." },
};

/* ── Numerology ────────────────────────────────────────── */
function digitSum(dateStr) {
    // dateStr: "YYYY-MM-DD"
    const digits = dateStr.replace(/-/g, "");
    return digits.split("").reduce((acc, d) => acc + parseInt(d, 10), 0);
}

function reduceToSingle(n) {
    while (n > 9) {
        n = String(n).split("").reduce((a, d) => a + parseInt(d, 10), 0);
    }
    return n;
}

/* ── Calculate ─────────────────────────────────────────── */
function calculate() {
    const bday1 = document.getElementById("bday1").value;
    const bday2 = document.getElementById("bday2").value;

    if (!bday1 || !bday2) {
        alert("Please enter both birthdays.");
        return;
    }

    const name1 = document.getElementById("name1").value.trim() || "Person One";
    const name2 = document.getElementById("name2").value.trim() || "Person Two";

    const raw1 = digitSum(bday1);
    const raw2 = digitSum(bday2);
    const num1 = reduceToSingle(raw1);
    const num2 = reduceToSingle(raw2);
    const combined = num1 + num2; // range 2–18

    const flower = FLOWERS[combined] || FLOWERS[9];

    // Populate results
    document.getElementById("res-emoji").textContent        = flower.emoji;
    document.getElementById("res-flower-name").textContent  = flower.name;
    document.getElementById("res-keyword").textContent      = flower.keywords;
    document.getElementById("res-message").textContent      = flower.msg;
    document.getElementById("res-name1").textContent        = name1;
    document.getElementById("res-name2").textContent        = name2;
    document.getElementById("res-num1").textContent         = num1;
    document.getElementById("res-num2").textContent         = num2;
    document.getElementById("score-pct").textContent        = flower.pct + "%";

    // Show section
    const resultsEl = document.getElementById("results");
    resultsEl.classList.remove("hidden");
    resultsEl.classList.add("visible");

    // Animate score bar (delayed so CSS transition fires)
    setTimeout(() => {
        document.getElementById("score-fill").style.width = flower.pct + "%";
    }, 100);

    // Scroll to results
    setTimeout(() => {
        resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 200);
}

/* ── Background: Stars + Petals ────────────────────────── */
const canvas = document.getElementById("bg-canvas");
const ctx    = canvas.getContext("2d");

let W, H;
let stars   = [];
let petals  = [];

function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
}

function initStars(n = 180) {
    stars = [];
    for (let i = 0; i < n; i++) {
        stars.push({
            x:    Math.random() * W,
            y:    Math.random() * H,
            r:    Math.random() * 1.2 + 0.2,
            a:    Math.random(),
            spd:  Math.random() * 0.003 + 0.001,
            dir:  Math.random() > 0.5 ? 1 : -1,
        });
    }
}

function initPetals(n = 18) {
    petals = [];
    for (let i = 0; i < n; i++) {
        petals.push(newPetal(true));
    }
}

function newPetal(spread = false) {
    return {
        x:     Math.random() * W,
        y:     spread ? Math.random() * H : -20,
        size:  Math.random() * 6 + 3,
        speedX: (Math.random() - 0.5) * 0.6,
        speedY: Math.random() * 0.8 + 0.3,
        rot:   Math.random() * Math.PI * 2,
        rotSpd: (Math.random() - 0.5) * 0.02,
        alpha: Math.random() * 0.4 + 0.1,
        hue:   Math.random() > 0.5 ? 340 : 20,  // pink or gold
    };
}

function drawStar(s) {
    s.a += s.spd * s.dir;
    if (s.a > 1 || s.a < 0) s.dir *= -1;
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,240,255,${s.a * 0.7})`;
    ctx.fill();
}

function drawPetal(p) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate(p.rot);
    ctx.beginPath();
    ctx.ellipse(0, 0, p.size, p.size * 0.5, 0, 0, Math.PI * 2);
    ctx.fillStyle = p.hue === 340
        ? `rgba(240,184,200,${p.alpha})`
        : `rgba(232,201,122,${p.alpha * 0.6})`;
    ctx.fill();
    ctx.restore();

    p.x     += p.speedX + Math.sin(p.y * 0.01) * 0.3;
    p.y     += p.speedY;
    p.rot   += p.rotSpd;

    if (p.y > H + 20) Object.assign(p, newPetal());
}

function loop() {
    ctx.clearRect(0, 0, W, H);

    // subtle radial gradient overlay
    const grad = ctx.createRadialGradient(W*0.3, H*0.3, 0, W*0.3, H*0.3, W*0.7);
    grad.addColorStop(0, "rgba(60,10,80,0.15)");
    grad.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    stars.forEach(drawStar);
    petals.forEach(drawPetal);

    requestAnimationFrame(loop);
}

window.addEventListener("resize", () => { resize(); initStars(); });
resize();
initStars();
initPetals();
loop();
