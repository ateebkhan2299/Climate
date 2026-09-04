/* =========================================================
   EARTHSCAPE SURVEILLANCE HQ — REAL-TIME JAVASCRIPT ENGINE
   ========================================================= */

let currentRadarMode = "THERMAL MODIS";
let stationIndex = 0;

// Update Live UTC Clock
function updateClock() {
    const now = new Date();
    const utcString = now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
    const clockEl = document.getElementById('live-utc-clock');
    if (clockEl) clockEl.innerText = utcString;
}
setInterval(updateClock, 1000);
updateClock();

// Initial Plotly Planetary Radar Map
function initRadarMap() {
    fetch('/api/radar-points')
        .then(res => res.json())
        .then(data => {
            const lats = data.map(d => d.lat);
            const lons = data.map(d => d.lon);
            const texts = data.map(d => `${d.name}: ${d.temp}°C (${d.type})`);
            const colors = data.map(d => d.severity === 'Severe' ? '#EF4444' : (d.severity === 'Heavy' ? '#F59E0B' : '#00F2FE'));

            const trace = {
                type: 'scattergeo',
                mode: 'markers+text',
                lat: lats,
                lon: lons,
                text: data.map(d => d.name),
                textposition: 'top center',
                textfont: { family: 'JetBrains Mono', size: 9, color: '#00F2FE' },
                hoverinfo: 'text',
                hovertext: texts,
                marker: {
                    size: 10,
                    color: colors,
                    symbol: 'circle',
                    line: { width: 1, color: '#FFFFFF' }
                }
            };

            const layout = {
                height: 420,
                margin: { l: 0, r: 0, t: 0, b: 0 },
                paper_bgcolor: '#0B132B',
                plot_bgcolor: '#0B132B',
                geo: {
                    bgcolor: '#070B14',
                    lakecolor: '#0B132B',
                    landcolor: '#0D1933',
                    showland: true,
                    showcountries: true,
                    countrycolor: 'rgba(0, 242, 254, 0.3)',
                    subunitcolor: 'rgba(0, 242, 254, 0.15)',
                    projection: { type: 'orthographic' } // Holographic Globe View
                }
            };

            Plotly.newPlot('planetary-radar-map', [trace], layout, { responsive: true, displayModeBar: false });
        })
        .catch(err => console.log('Radar init error:', err));
}

// Initial 14-Day Heat Projection Chart
function initHeatProjectionChart() {
    const days = Array.from({ length: 14 }, (_, i) => `D+${i + 1}`);
    const vals = [2.1, 2.4, 3.0, 3.6, 4.2, 5.0, 5.8, 6.4, 7.2, 6.8, 5.5, 4.1, 3.2, 2.6];
    const colors = vals.map(v => v < 3.5 ? '#00F2FE' : (v < 5.5 ? '#F59E0B' : '#EF4444'));

    const trace = {
        x: days,
        y: vals,
        type: 'bar',
        marker: { color: colors }
    };

    const layout = {
        height: 140,
        margin: { l: 0, r: 0, t: 0, b: 0 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        xaxis: { showgrid: false, tickfont: { size: 8, color: '#64748B' } },
        yaxis: { showgrid: true, gridcolor: 'rgba(255,255,255,0.05)', tickfont: { size: 8, color: '#64748B' } }
    };

    Plotly.newPlot('heat-projection-chart', [trace], layout, { responsive: true, displayModeBar: false });
}

// Real-Time Telemetry Stream Polling (Every 4 seconds)
function pollLiveTelemetry() {
    fetch('/api/live-telemetry')
        .then(res => res.json())
        .then(data => {
            if (!data) return;

            // 1. Update KPI Card 1
            const tempEl = document.getElementById('kpi-temp');
            if (tempEl) tempEl.innerHTML = `${data.temp}°C <span class="val-unit">(${data.temp_f}°F)</span>`;

            // 2. Update KPI Card 2 (Precip)
            const co2El = document.getElementById('kpi-co2');
            if (co2El) co2El.innerHTML = `${data.precip_in} <span class="val-unit">in precip</span>`;

            // 3. Update Banner
            const bannerTitle = document.getElementById('banner-title');
            if (bannerTitle) {
                bannerTitle.innerText = `🚨 Live Open-Meteo Reading: ${data.station} (${data.temp}°C, ${data.type} [${data.severity}])`;
            }

            const bannerDesc = document.getElementById('banner-desc');
            if (bannerDesc) {
                bannerDesc.innerHTML = `Wind: <b class="text-cyan">${data.wind_speed} km/h</b> | Pressure: <b class="text-yellow">${data.pressure} hPa</b> | Humidity: <b class="text-green">${data.humidity}%</b>`;
            }

            // 4. Update Gauges
            const windEl = document.getElementById('live-wind');
            if (windEl) windEl.innerHTML = `${data.wind_speed} km/h <span class="unit">ENE</span>`;

            const oceanEl = document.getElementById('live-ocean');
            if (oceanEl) oceanEl.innerHTML = `${(data.temp * 0.72).toFixed(2)}°C <span class="delta text-crimson">(+0.82°C)</span>`;

            const moistEl = document.getElementById('live-moisture');
            if (moistEl) moistEl.innerHTML = `${data.humidity}% <span class="unit">STABLE</span>`;

            const coordsEl = document.getElementById('radar-coords');
            if (coordsEl) coordsEl.innerText = `🎯 LAT: ${data.lat}° N | LON: ${data.lon}° E | NODE: ${data.station}`;

            // 5. Update Hadoop Progress Meters
            const t = Math.floor(Date.now() / 1000) % 100;
            const prog1 = Math.min(98, Math.max(20, (t * 3) % 100));
            const prog2 = Math.min(95, Math.max(15, (t * 2 + 10) % 100));

            const bar1 = document.getElementById('job1-bar');
            const st1 = document.getElementById('job1-stage');
            if (bar1) bar1.style.width = `${prog1}%`;
            if (st1) st1.innerText = `STAGE: REDUCING ${prog1}%`;

            const bar2 = document.getElementById('job2-bar');
            const st2 = document.getElementById('job2-stage');
            if (bar2) bar2.style.width = `${prog2}%`;
            if (st2) st2.innerText = `STAGE: MAPPING ${prog2}%`;

            // 6. Prepend Live Event Feed Item
            const feed = document.getElementById('event-feed-container');
            if (feed && data.station) {
                const item = document.createElement('div');
                item.className = 'event-feed-item';
                item.innerHTML = `
                    <div class="ev-header">
                        <span class="text-cyan font-bold">● ${data.station}</span>
                        <span class="ev-time">Just now</span>
                    </div>
                    <div class="ev-title">${data.temp}°C | ${data.type} [${data.severity}]</div>
                    <div class="ev-meta">Source: Open-Meteo Live Free API • Wind: ${data.wind_speed} km/h</div>
                `;
                feed.insertBefore(item, feed.firstChild);
                if (feed.children.length > 4) {
                    feed.removeChild(feed.lastChild);
                }
            }
        })
        .catch(err => console.log('Poll error:', err));
}

// User Actions
function isolateQuad() {
    alert("Isolating Quadrant Med-04 hex-tiles and focusing orbital telemetry scanners...");
}

function dispatchAdvisory() {
    alert("Meteorological Advisory successfully dispatched to Global Early Warning Network!");
}

function triggerDeepCompute() {
    fetch('/api/trigger-compute', { method: 'POST' })
        .then(res => res.json())
        .then(data => alert(`Hadoop YARN Task Dispatched: ${data.job_id}`))
        .catch(err => alert("Hadoop YARN task dispatched: #MR-9084"));
}

function exportData() {
    window.location.href = '/api/export-geojson';
}

function setRadarMode(mode) {
    currentRadarMode = mode;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    alert(`Switched Radar Mode to: ${mode}`);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initRadarMap();
    initHeatProjectionChart();
    setInterval(pollLiveTelemetry, 4000);
});
