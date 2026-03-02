const baseURL = "http://127.0.0.1:5000";
let jwtToken = null;
let alertChart = null;

/* ===================== LOGIN ===================== */
document.getElementById("login-form").onsubmit = async (e) => {
    e.preventDefault();

    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const res = await fetch(`${baseURL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (res.ok) {
        jwtToken = data.token;
        alert("Login successful");
        showDashboard();
        loadDashboard();
    } else {
        alert(data.msg || "Login failed");
    }
};

/* ===================== REGISTER ===================== */
document.getElementById("register-form").onsubmit = async (e) => {
    e.preventDefault();

    const username = document.getElementById("reg-username").value;
    const password = document.getElementById("reg-password").value;

    const res = await fetch(`${baseURL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    alert(data.msg);
};

/* ===================== LOGOUT ===================== */
document.getElementById("logout-btn").onclick = () => {
    jwtToken = null;
    document.getElementById("auth-screen").classList.remove("hidden");
    document.getElementById("dashboard-screen").classList.add("hidden");
};

/* ===================== SHOW DASHBOARD ===================== */
function showDashboard() {
    document.getElementById("auth-screen").classList.add("hidden");
    document.getElementById("dashboard-screen").classList.remove("hidden");
}

/* ===================== LOAD DASHBOARD ===================== */
async function loadDashboard() {
    await loadAlerts();
    await loadHistory();
}

/* ===================== LOAD ALERTS ===================== */
async function loadAlerts() {
    const res = await fetch(`${baseURL}/alerts`, {
        headers: {
            Authorization: "Bearer " + jwtToken
        }
    });

    const alerts = await res.json();
    const table = document.getElementById("alertsTable");
    table.innerHTML = "";

    alerts.forEach(a => {
        const severity =
            a.alert_type.includes("failed") ? "HIGH" :
            a.alert_type.includes("suspicious") ? "HIGH" :
            a.alert_type.includes("login") ? "MEDIUM" :
            "LOW";

        table.innerHTML += `
            <tr>
                <td>${a.id}</td>
                <td>${a.username || "-"}</td>
                <td>${a.alert_type}</td>
                <td>${a.description}</td>
                <td><span class="badge ${severity}">${severity}</span></td>
                <td>${a.timestamp}</td>
            </tr>
        `;
    });

    drawChart(alerts);
}

/* ===================== LOAD LOGIN HISTORY ===================== */
async function loadHistory() {
    const res = await fetch(`${baseURL}/login-history`, {
        headers: {
            Authorization: "Bearer " + jwtToken
        }
    });

    const history = await res.json();
    const table = document.getElementById("historyTable");
    table.innerHTML = "";

    history.forEach(h => {
        const severity = h.status === "failed" ? "HIGH" : "LOW";

        table.innerHTML += `
            <tr>
                <td>${h.username}</td>
                <td>${h.status}</td>
                <td><span class="badge ${severity}">${severity}</span></td>
                <td>${h.timestamp}</td>
            </tr>
        `;
    });
}

/* ===================== ALERT CHART ===================== */
function drawChart(alerts) {
    const counts = {};

    alerts.forEach(a => {
        counts[a.alert_type] = (counts[a.alert_type] || 0) + 1;
    });

    const ctx = document.getElementById("alertsChart").getContext("2d");

    if (alertChart) {
        alertChart.destroy();
    }

    alertChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: Object.keys(counts),
            datasets: [{
                label: "Alert Count",
                data: Object.values(counts)
            }]
        },
        options: {
            responsive: true
        }
    });
}

/* ===================== MANUAL ALERT ===================== */
async function createManualAlert() {
    const data = {
        username: document.getElementById("m_username").value,
        alert_type: document.getElementById("m_type").value,
        description: document.getElementById("m_desc").value
    };

    await fetch(`${baseURL}/manual-alert`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + jwtToken
        },
        body: JSON.stringify(data)
    });

    document.getElementById("m_username").value = "";
    document.getElementById("m_type").value = "";
    document.getElementById("m_desc").value = "";

    loadAlerts();
}