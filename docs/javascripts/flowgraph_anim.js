document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("grc-animation-root");
    if (!container) return;

    // Define Block Layout States
    const BLOCKS = [
        {
            id: "options",
            title: "Options",
            sub: "id: top_block",
            type: "header",
            w: 160, h: 70,
            messy: { x: 340, y: 320 },
            clean: { x: 20, y: 20 },
            inPorts: [],
            outPorts: []
        },
        {
            id: "var_samp",
            title: "Variable",
            sub: "samp_rate: 2M",
            type: "var",
            w: 150, h: 60,
            messy: { x: 50, y: 350 },
            clean: { x: 200, y: 20 },
            inPorts: [],
            outPorts: []
        },
        {
            id: "var_cutoff",
            title: "Variable",
            sub: "cutoff: 350k",
            type: "var",
            w: 150, h: 60,
            messy: { x: 620, y: 20 },
            clean: { x: 370, y: 20 },
            inPorts: [],
            outPorts: []
        },
        {
            id: "sig_src",
            title: "Signal Source",
            sub: "Cosine (10 kHz)",
            type: "source",
            w: 160, h: 90,
            messy: { x: 520, y: 200 },
            clean: { x: 20, y: 180 },
            inPorts: [],
            outPorts: [{ id: "out", y: 45 }]
        },
        {
            id: "throttle",
            title: "Throttle",
            sub: "Rate: samp_rate",
            type: "proc",
            w: 140, h: 75,
            messy: { x: 30, y: 150 },
            clean: { x: 230, y: 190 },
            inPorts: [{ id: "in", y: 38 }],
            outPorts: [{ id: "out", y: 38 }]
        },
        {
            id: "lpf",
            title: "Low Pass Filter",
            sub: "Decim: 1 | Cutoff: 350k",
            type: "filter",
            w: 170, h: 90,
            messy: { x: 280, y: 130 },
            clean: { x: 420, y: 180 },
            inPorts: [{ id: "in", y: 45 }],
            outPorts: [{ id: "out", y: 45 }]
        },
        {
            id: "time_sink",
            title: "QT GUI Time Sink",
            sub: "1024 Points",
            type: "sink",
            w: 160, h: 80,
            messy: { x: 120, y: 20 },
            clean: { x: 640, y: 120 },
            inPorts: [{ id: "in", y: 40 }],
            outPorts: []
        },
        {
            id: "freq_sink",
            title: "QT GUI Freq Sink",
            sub: "FFT Size: 1024",
            type: "sink",
            w: 160, h: 80,
            messy: { x: 480, y: 360 },
            clean: { x: 640, y: 250 },
            inPorts: [{ id: "in", y: 40 }],
            outPorts: []
        }
    ];

    const WIRES = [
        { from: "sig_src", outIdx: 0, to: "throttle", inIdx: 0 },
        { from: "throttle", outIdx: 0, to: "lpf", inIdx: 0 },
        { from: "lpf", outIdx: 0, to: "time_sink", inIdx: 0 },
        { from: "lpf", outIdx: 0, to: "freq_sink", inIdx: 0 }
    ];

    let isArranged = false;
    let autoLoopTimer = null;

    // Build SVG Canvas
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("viewBox", "0 0 830 380");
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "100%");
    svg.style.borderRadius = "8px";

    // Wires Layer
    const wiresGroup = document.createElementNS(svgNS, "g");
    wiresGroup.setAttribute("class", "wires-layer");
    svg.appendChild(wiresGroup);

    // Blocks Layer
    const blocksGroup = document.createElementNS(svgNS, "g");
    blocksGroup.setAttribute("class", "blocks-layer");
    svg.appendChild(blocksGroup);

    container.innerHTML = "";
    container.appendChild(svg);

    // Map DOM elements
    const blockElements = new Map();
    const wireElements = [];

    // Colors per type
    const TYPE_COLORS = {
        header: { header: "#3b3e52", body: "#2a2c3d", text: "#e2e8f0" },
        var: { header: "#4338ca", body: "#242542", text: "#c7d2fe" },
        source: { header: "#1d4ed8", body: "#1e293b", text: "#bfdbfe" },
        proc: { header: "#0f766e", body: "#132a2f", text: "#99f6e4" },
        filter: { header: "#047857", body: "#112e25", text: "#a7f3d0" },
        sink: { header: "#b91c1c", body: "#321d24", text: "#fecaca" }
    };

    // Create Block DOM elements
    BLOCKS.forEach(b => {
        const g = document.createElementNS(svgNS, "g");
        g.setAttribute("class", "grc-block");
        g.style.transition = "transform 1.1s cubic-bezier(0.34, 1.4, 0.64, 1)";
        g.style.cursor = "pointer";

        const colors = TYPE_COLORS[b.type] || TYPE_COLORS.proc;

        // Shadow & Body
        const rect = document.createElementNS(svgNS, "rect");
        rect.setAttribute("width", b.w);
        rect.setAttribute("height", b.h);
        rect.setAttribute("rx", 6);
        rect.setAttribute("fill", colors.body);
        rect.setAttribute("stroke", "#4b5563");
        rect.setAttribute("stroke-width", "1.5");
        rect.setAttribute("filter", "drop-shadow(0 4px 6px rgba(0,0,0,0.3))");
        g.appendChild(rect);

        // Header
        const headerRect = document.createElementNS(svgNS, "path");
        headerRect.setAttribute("d", `M 0 6 Q 0 0 6 0 L ${b.w - 6} 0 Q ${b.w} 0 ${b.w} 6 L ${b.w} 24 L 0 24 Z`);
        headerRect.setAttribute("fill", colors.header);
        g.appendChild(headerRect);

        // Title
        const titleText = document.createElementNS(svgNS, "text");
        titleText.setAttribute("x", 10);
        titleText.setAttribute("y", 16);
        titleText.setAttribute("fill", "#ffffff");
        titleText.setAttribute("font-size", "11px");
        titleText.setAttribute("font-weight", "bold");
        titleText.setAttribute("font-family", "sans-serif");
        titleText.textContent = b.title;
        g.appendChild(titleText);

        // Subtitle / Params
        const subText = document.createElementNS(svgNS, "text");
        subText.setAttribute("x", 10);
        subText.setAttribute("y", 44);
        subText.setAttribute("fill", colors.text);
        subText.setAttribute("font-size", "9.5px");
        subText.setAttribute("font-family", "monospace");
        subText.textContent = b.sub;
        g.appendChild(subText);

        // In Ports
        b.inPorts.forEach(p => {
            const port = document.createElementNS(svgNS, "rect");
            port.setAttribute("x", -7);
            port.setAttribute("y", p.y - 7);
            port.setAttribute("width", 14);
            port.setAttribute("height", 14);
            port.setAttribute("rx", 2);
            port.setAttribute("fill", "#38bdf8");
            port.setAttribute("stroke", "#0284c7");
            port.setAttribute("stroke-width", "1.5");
            g.appendChild(port);
        });

        // Out Ports
        b.outPorts.forEach(p => {
            const port = document.createElementNS(svgNS, "rect");
            port.setAttribute("x", b.w - 7);
            port.setAttribute("y", p.y - 7);
            port.setAttribute("width", 14);
            port.setAttribute("height", 14);
            port.setAttribute("rx", 2);
            port.setAttribute("fill", "#4ade80");
            port.setAttribute("stroke", "#16a34a");
            port.setAttribute("stroke-width", "1.5");
            g.appendChild(port);
        });

        blocksGroup.appendChild(g);
        blockElements.set(b.id, { g, block: b });
    });

    // Create Wire paths
    WIRES.forEach(w => {
        const path = document.createElementNS(svgNS, "path");
        path.setAttribute("fill", "none");
        path.setAttribute("stroke", "#4ade80");
        path.setAttribute("stroke-width", "2.5");
        path.setAttribute("stroke-linecap", "round");
        path.style.transition = "d 1.1s cubic-bezier(0.34, 1.4, 0.64, 1), stroke 0.3s";
        wiresGroup.appendChild(path);
        wireElements.push({ path, wire: w });
    });

    // Update positions
    function updateLayout(arranged, smooth = true) {
        isArranged = arranged;

        BLOCKS.forEach(b => {
            const el = blockElements.get(b.id);
            const pos = arranged ? b.clean : b.messy;
            el.g.style.transform = `translate(${pos.x}px, ${pos.y}px)`;
        });

        // Update Wires
        WIRES.forEach((w, idx) => {
            const fromBlock = BLOCKS.find(b => b.id === w.from);
            const toBlock = BLOCKS.find(b => b.id === w.to);
            const fromPos = arranged ? fromBlock.clean : fromBlock.messy;
            const toPos = arranged ? toBlock.clean : toBlock.messy;

            const x1 = fromPos.x + fromBlock.w + 7;
            const y1 = fromPos.y + fromBlock.outPorts[w.outIdx].y;
            const x2 = toPos.x - 7;
            const y2 = toPos.y + toBlock.inPorts[w.inIdx].y;

            let pathD;
            if (arranged) {
                // Clean orthogonal S-curve
                const midX = (x1 + x2) / 2;
                pathD = `M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`;
                wireElements[idx].path.setAttribute("stroke", "#4ade80");
            } else {
                // Tangled diagonal messy wire
                const ctrlX1 = x1 + (x2 - x1) * 0.2 + (idx % 2 === 0 ? 50 : -40);
                const ctrlY1 = y1 + (y2 - y1) * 0.8 + (idx % 2 === 0 ? -60 : 70);
                pathD = `M ${x1} ${y1} Q ${ctrlX1} ${ctrlY1}, ${x2} ${y2}`;
                wireElements[idx].path.setAttribute("stroke", "#f87171");
            }
            wireElements[idx].path.setAttribute("d", pathD);
        });

        // Update Status Badge & Button
        const statusBadge = document.getElementById("grc-status-badge");
        const triggerBtn = document.getElementById("grc-trigger-btn");
        if (statusBadge) {
            if (arranged) {
                statusBadge.className = "grc-badge active";
                statusBadge.innerHTML = "✨ ELK Auto-Arranged (Grid Snapped: 8px)";
            } else {
                statusBadge.className = "grc-badge";
                statusBadge.innerHTML = "⚠️ Messy Flowgraph (Unarranged)";
            }
        }
        if (triggerBtn) {
            triggerBtn.innerText = arranged ? "↺ Reset to Messy" : "⚡ Auto-Arrange (Ctrl+Shift+A)";
        }
    }

    // Initial render
    updateLayout(false, false);

    // Loop cycle: Messy (2.5s) -> Arrange (4s) -> Loop
    function runLoop() {
        autoLoopTimer = setTimeout(() => {
            updateLayout(true);
            autoLoopTimer = setTimeout(() => {
                updateLayout(false);
                runLoop();
            }, 5000);
        }, 3000);
    }

    runLoop();

    // Manual Click Handler
    const triggerBtn = document.getElementById("grc-trigger-btn");
    if (triggerBtn) {
        triggerBtn.addEventListener("click", () => {
            if (autoLoopTimer) clearTimeout(autoLoopTimer);
            updateLayout(!isArranged);
            runLoop();
        });
    }
});
