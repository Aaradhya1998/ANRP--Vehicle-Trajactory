const API_BASE = "http://localhost:8000";

function updateStatus(isOnline) {
  const dot = document.getElementById("status-dot");
  const text = document.getElementById("status-text");
  if (!dot || !text) return;
  if (isOnline) {
    dot.className = "status-dot online";
    text.textContent = "API Online";
  } else {
    dot.className = "status-dot offline";
    text.textContent = "API Offline";
  }
}

async function fetchDetections() {
  const tbody = document.getElementById("detections-tbody");
  try {
    const res = await fetch(`${API_BASE}/detections`);
    if (!res.ok) throw new Error("API Error");
    const data = await res.json();
    updateStatus(true);
    
    if (!data || data.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="empty-cell">No detections recorded yet.</td></tr>`;
      return;
    }

    const rows = [...data].reverse();
    tbody.innerHTML = rows.map(d => `
      <tr>
        <td><code>${d.event_id || '-'}</code></td>
        <td><strong>${d.plate_number || '-'}</strong></td>
        <td>${d.camera_id || '-'}</td>
        <td>${d.latitude !== undefined ? Number(d.latitude).toFixed(4) : '-'}</td>
        <td>${d.longitude !== undefined ? Number(d.longitude).toFixed(4) : '-'}</td>
        <td>${d.timestamp || '-'}</td>
        <td>${d.confidence ? (Number(d.confidence) * 100).toFixed(0) + '%' : '-'}</td>
      </tr>
    `).join("");
  } catch (err) {
    updateStatus(false);
    tbody.innerHTML = `<tr><td colspan="7" class="empty-cell error-cell">Unable to fetch detections.</td></tr>`;
  }
}

async function fetchAlerts() {
  const consoleEl = document.getElementById("alert-console");
  const countBadge = document.getElementById("alert-count");
  try {
    const res = await fetch(`${API_BASE}/alerts`);
    if (!res.ok) throw new Error("API Error");
    const alerts = await res.json();
    
    countBadge.textContent = `${alerts.length} active`;
    countBadge.className = alerts.length > 0 ? "badge badge-high" : "badge badge-neutral";

    if (!alerts || alerts.length === 0) {
      consoleEl.innerHTML = `<p class="empty-msg">No unacknowledged alerts.</p>`;
      return;
    }

    consoleEl.innerHTML = alerts.map(a => {
      const typeClass = (a.alert_type || '').toLowerCase();
      return `
        <div class="alert-card alert-${typeClass}">
          <div class="alert-info">
            <span class="alert-type">${a.alert_type}</span>
            <span class="alert-detail">Plate: <strong>${a.plate_number}</strong> | Camera: <strong>${a.camera_id}</strong></span>
            <span class="alert-time">${a.timestamp}</span>
          </div>
          <button class="ack-btn" onclick="acknowledgeAlert('${a.alert_id}')">Acknowledge</button>
        </div>
      `;
    }).join("");
  } catch (err) {
    consoleEl.innerHTML = `<p class="empty-msg error-cell">Error connecting to alert service.</p>`;
  }
}

async function acknowledgeAlert(alertId) {
  try {
    const res = await fetch(`${API_BASE}/acknowledge/${alertId}`, { method: "POST" });
    if (res.ok) {
      fetchAlerts();
    }
  } catch (err) {
    console.error("Failed to acknowledge alert:", err);
  }
}

function calculateSpeed(lat1, lon1, t1, lat2, lon2, t2) {
  if (!lat1 || !lat2 || !t1 || !t2) return "N/A";
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  const distKm = R * c;
  const timeSec = (new Date(t2) - new Date(t1)) / 1000;
  if (isNaN(timeSec) || timeSec <= 0) return "0 km/h";
  const speed = Math.round((distKm / timeSec) * 3600);
  return `${speed} km/h`;
}

async function searchPlate(plate) {
  const tbody = document.getElementById("trajectory-tbody");
  if (!plate) return;
  tbody.innerHTML = `<tr><td colspan="3" class="empty-cell">Searching...</td></tr>`;
  
  try {
    const res = await fetch(`${API_BASE}/trajectory/${encodeURIComponent(plate.trim().toUpperCase())}`);
    if (!res.ok) throw new Error("API Error");
    const records = await res.json();
    
    if (!records || records.length === 0) {
      tbody.innerHTML = `<tr><td colspan="3" class="empty-cell">No trajectory history found for plate "${plate}".</td></tr>`;
      return;
    }

    tbody.innerHTML = records.map((r, i) => {
      let speedStr = "N/A";
      if (i > 0) {
        const prev = records[i - 1];
        speedStr = calculateSpeed(prev.latitude, prev.longitude, prev.timestamp, r.latitude, r.longitude, r.timestamp);
      }
      return `
        <tr>
          <td><strong>${r.camera_id}</strong></td>
          <td>${r.timestamp}</td>
          <td><span class="speed-badge">${speedStr}</span></td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="3" class="empty-cell error-cell">Failed to search trajectory.</td></tr>`;
  }
}

async function fetchDensity() {
  const container = document.getElementById("density-container");
  try {
    const res = await fetch(`${API_BASE}/density`);
    if (!res.ok) throw new Error("API Error");
    const densityMap = await res.json();
    
    const cameras = Object.keys(densityMap);
    if (cameras.length === 0) {
      container.innerHTML = `<p class="empty-msg">No active camera metrics.</p>`;
      return;
    }

    container.innerHTML = cameras.map(cam => {
      const level = densityMap[cam]; // LOW, MED, HIGH, MEDIUM
      let badgeClass = "badge-low";
      if (level === "HIGH") badgeClass = "badge-high";
      else if (level === "MED" || level === "MEDIUM") badgeClass = "badge-med";
      
      return `
        <div class="density-card">
          <span class="density-cam">${cam}</span>
          <span class="badge ${badgeClass}">${level}</span>
        </div>
      `;
    }).join("");
  } catch (err) {
    container.innerHTML = `<p class="empty-msg error-cell">Density metrics offline.</p>`;
  }
}

function startAutoRefresh() {
  const refreshAll = () => {
    fetchDetections();
    fetchAlerts();
    fetchDensity();
  };
  refreshAll();
  setInterval(refreshAll, 5000);
}

document.addEventListener("DOMContentLoaded", () => {
  startAutoRefresh();
  
  const searchForm = document.getElementById("search-form");
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const val = document.getElementById("plate-input").value;
      searchPlate(val);
    });
  }
});
