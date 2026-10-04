const canvas = document.getElementById('lifeblood-canvas');
const ctx = canvas.getContext('2d');
let width, height, dpr;
let animationId;
let time = 0;
let reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function resize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = rect.width;
    height = rect.height;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

function drawGlow(x, y, r, color, alpha = 1) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, color.replace('1)', `${alpha})`));
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
}

function drawBloodBag(x, y, w, h) {
    ctx.save();
    ctx.translate(x, y);

    const bagGrad = ctx.createLinearGradient(0, 0, w, 0);
    bagGrad.addColorStop(0, 'rgba(139,10,31,0.35)');
    bagGrad.addColorStop(0.5, 'rgba(224,36,58,0.18)');
    bagGrad.addColorStop(1, 'rgba(139,10,31,0.35)');
    ctx.fillStyle = bagGrad;
    ctx.strokeStyle = 'rgba(255,255,255,0.22)';
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    ctx.roundRect(0, 0, w, h, 14);
    ctx.fill();
    ctx.stroke();

    const liquidH = h * (0.45 + Math.sin(time * 0.8) * 0.06);
    const liq = ctx.createLinearGradient(0, h - liquidH, 0, h);
    liq.addColorStop(0, 'rgba(224,36,58,0.55)');
    liq.addColorStop(1, 'rgba(120,8,24,0.85)');
    ctx.fillStyle = liq;
    ctx.beginPath();
    ctx.roundRect(6, h - liquidH + 6, w - 12, liquidH - 12, 10);
    ctx.fill();

    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.font = '600 11px "Segoe UI", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('BLOOD', w / 2, h * 0.28);
    ctx.fillText('DONATION', w / 2, h * 0.28 + 16);
    ctx.fillStyle = 'rgba(255,255,255,0.7)';
    ctx.font = '500 20px "Segoe UI", sans-serif';
    ctx.fillText('O+', w / 2, h * 0.45);
    ctx.fillStyle = 'rgba(255,255,255,0.55)';
    ctx.font = '500 10px "Segoe UI", sans-serif';
    ctx.fillText('SAVE LIVES', w / 2, h * 0.63);

    ctx.restore();
}

function drawTube(x1, y1, x2, y2) {
    ctx.save();
    ctx.strokeStyle = 'rgba(255,255,255,0.18)';
    ctx.lineWidth = 7;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.bezierCurveTo(x1 + 40, y1 + 40, x2 - 40, y2 - 40, x2, y2);
    ctx.stroke();

    ctx.strokeStyle = 'rgba(255,255,255,0.32)';
    ctx.lineWidth = 3;
    ctx.stroke();
    ctx.restore();
}

class Particle {
    constructor(path) {
        this.path = path;
        this.t = 0;
        this.speed = 0.004 + Math.random() * 0.006;
        this.size = 1.2 + Math.random() * 2.4;
        this.opacity = 0.5 + Math.random() * 0.5;
    }
    update() {
        if (!reducedMotion) {
            this.t += this.speed;
        }
        if (this.t > 1) this.t = 0;
    }
    draw() {
        const p = this.path.getPoint(this.t);
        const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, this.size * 3);
        g.addColorStop(0, `rgba(255,40,60,${this.opacity})`);
        g.addColorStop(1, 'rgba(255,40,60,0)');
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(p.x, p.y, this.size * 3, 0, Math.PI * 2);
        ctx.fill();
    }
}

class BezierPath {
    constructor(x1, y1, cp1x, cp1y, cp2x, cp2y, x2, y2) {
        this.x1 = x1; this.y1 = y1;
        this.cp1x = cp1x; this.cp1y = cp1y;
        this.cp2x = cp2x; this.cp2y = cp2y;
        this.x2 = x2; this.y2 = y2;
    }
    getPoint(t) {
        const mt = 1 - t;
        return {
            x: mt*mt*mt*this.x1 + 3*mt*mt*t*this.cp1x + 3*mt*t*t*this.cp2x + t*t*t*this.x2,
            y: mt*mt*mt*this.y1 + 3*mt*mt*t*this.cp1y + 3*mt*t*t*this.cp2y + t*t*t*this.y2,
        };
    }
}

class Heart {
    constructor(x, y, size) {
        this.x = x; this.y = y; this.size = size;
        this.beat = 0;
    }
    update() {
        this.beat += 0.03;
    }
    draw() {
        const pulse = Math.sin(this.beat) > 0.85 ? 1.15 : 1;
        const glow = Math.sin(this.beat) > 0.85 ? 0.45 : 0.2;
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.scale(pulse, pulse);
        drawGlow(0, 0, this.size * 2.2, 'rgba(224,36,58,1)', glow);
        ctx.fillStyle = '#e0243a';
        ctx.beginPath();
        const s = this.size;
        ctx.moveTo(0, s * 0.35);
        ctx.bezierCurveTo(-s * 0.6, -s * 0.2, -s * 0.9, -s * 0.7, 0, -s * 0.35);
        ctx.bezierCurveTo(s * 0.9, -s * 0.7, s * 0.6, -s * 0.2, 0, s * 0.35);
        ctx.fill();
        ctx.restore();
    }
}

function drawBody(x, y, w, h) {
    ctx.save();
    ctx.translate(x, y);
    ctx.strokeStyle = 'rgba(56,189,248,0.35)';
    ctx.lineWidth = 1.6;
    ctx.shadowColor = 'rgba(56,189,248,0.35)';
    ctx.shadowBlur = 12;
    ctx.beginPath();
    ctx.roundRect(0, 0, w, h, 18);
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.restore();
}

function drawECG(x, y, w) {
    ctx.save();
    ctx.strokeStyle = 'rgba(56,189,248,0.55)';
    ctx.lineWidth = 1.4;
    ctx.shadowColor = 'rgba(56,189,248,0.5)';
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.moveTo(x, y);
    for (let i = 0; i < w; i += 2) {
        const beat = Math.sin(time * 1.6 + i * 0.04) > 0.92 ? -14 : 0;
        ctx.lineTo(x + i, y + beat + Math.sin(i * 0.12) * 2);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.restore();
}

let particles = [];
let tubePath;

function initScene() {
    resize();
    particles = [];
    const bagX = width * 0.08;
    const bagY = height * 0.12;
    const bagW = 90;
    const bagH = 140;
    const tubeStart = { x: bagX + bagW / 2, y: bagY + bagH };
    const tubeEnd = { x: width * 0.62, y: height * 0.55 };
    tubePath = new BezierPath(
        tubeStart.x, tubeStart.y,
        tubeStart.x + 30, tubeStart.y + 50,
        tubeEnd.x - 50, tubeEnd.y - 30,
        tubeEnd.x, tubeEnd.y
    );
    for (let i = 0; i < 35; i++) {
        particles.push(new Particle(tubePath));
    }
}

function animate() {
    ctx.clearRect(0, 0, width, height);
    time += 0.016;

    const bagX = width * 0.08;
    const bagY = height * 0.12;
    const bagW = 90;
    const bagH = 140;
    drawBloodBag(bagX, bagY, bagW, bagH);

    const tubeStart = { x: bagX + bagW / 2, y: bagY + bagH };
    const tubeEnd = { x: width * 0.62, y: height * 0.55 };
    tubePath = new BezierPath(
        tubeStart.x, tubeStart.y,
        tubeStart.x + 30, tubeStart.y + 50,
        tubeEnd.x - 50, tubeEnd.y - 30,
        tubeEnd.x, tubeEnd.y
    );
    drawTube(tubeStart.x, tubeStart.y, tubeEnd.x, tubeEnd.y);

    particles.forEach(p => {
        p.update();
        p.draw();
    });

    const bodyX = width * 0.38;
    const bodyY = height * 0.18;
    const bodyW = width * 0.28;
    const bodyH = height * 0.72;
    drawBody(bodyX, bodyY, bodyW, bodyH);

    const heartX = bodyX + bodyW * 0.5;
    const heartY = bodyY + bodyH * 0.35;
    const heart = new Heart(heartX, heartY, 18);
    heart.beat = time;
    heart.update();
    heart.draw();

    drawECG(bodyX + bodyW * 0.1, bodyY + bodyH * 0.18, bodyW * 0.8);

    animationId = requestAnimationFrame(animate);
}

window.addEventListener('resize', () => {
    resize();
    initScene();
});

if (reducedMotion) {
    const staticDraw = () => {
        ctx.clearRect(0, 0, width, height);
        const bagX = width * 0.08;
        const bagY = height * 0.12;
        drawBloodBag(bagX, bagY, 90, 140);
        const tubeStart = { x: bagX + 45, y: bagY + 140 };
        const tubeEnd = { x: width * 0.62, y: height * 0.55 };
        drawTube(tubeStart.x, tubeStart.y, tubeEnd.x, tubeEnd.y);
        const bodyX = width * 0.38;
        const bodyY = height * 0.18;
        const bodyW = width * 0.28;
        const bodyH = height * 0.72;
        drawBody(bodyX, bodyY, bodyW, bodyH);
        const heart = new Heart(bodyX + bodyW * 0.5, bodyY + bodyH * 0.35, 18);
        heart.draw();
        drawECG(bodyX + bodyW * 0.1, bodyY + bodyH * 0.18, bodyW * 0.8);
    };
    resize();
    staticDraw();
} else {
    initScene();
    animate();
}

window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', e => {
    reducedMotion = e.matches;
    if (reducedMotion) {
        cancelAnimationFrame(animationId);
        resize();
        const bagX = width * 0.08;
        const bagY = height * 0.12;
        drawBloodBag(bagX, bagY, 90, 140);
    } else {
        initScene();
        animate();
    }
});
