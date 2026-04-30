<svelte:head>
	<title>HIDS | Dashboard</title>
</svelte:head>
<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { fade, fly } from 'svelte/transition';

	const baseURL = 'http://127.0.0.1:5000';

	let alerts = $state<any[]>([]);
	let history = $state<any[]>([]);

	let m_username = $state('');
	let m_type = $state('');
	let m_desc = $state('');

	let chartCanvas: HTMLCanvasElement | null = null;
	let chart: any = null;

	function getToken() {
		return localStorage.getItem('token');
	}

	function severity(type: string) {
		if (type.includes('failed') || type.includes('suspicious')) return 'high';
		if (type.includes('login')) return 'medium';
		return 'low';
	}

	async function loadData() {
		const token = getToken();
		if (!token) return goto('/');

		const headers = { Authorization: `Bearer ${token}` };

		const a = await fetch(`${baseURL}/alerts`, { headers });
		alerts = await a.json();

		const h = await fetch(`${baseURL}/login-history`, { headers });
		history = await h.json();

		drawChart();
	}

	async function drawChart() {
		if (!chartCanvas) return;

		const mod = await import('chart.js/auto');
		const { Chart } = mod as any;

		const counts: Record<string, number> = {};
		alerts.forEach(a => {
			counts[a.alert_type] = (counts[a.alert_type] || 0) + 1;
		});

		if (chart) chart.destroy();

		chart = new Chart(chartCanvas, {
			type: 'bar',
			data: {
				labels: Object.keys(counts),
				datasets: [{
					label: 'Alerts',
					data: Object.values(counts),
					borderRadius: 8
				}]
			},
			options: {
				plugins: { legend: { display: false } },
				scales: {
					x: { grid: { display: false } },
					y: { grid: { color: '#eee' } }
				}
			}
		});
	}

	async function createAlert() {
		const token = getToken();

		await fetch(`${baseURL}/manual-alert`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${token}`
			},
			body: JSON.stringify({
				username: m_username,
				alert_type: m_type,
				description: m_desc
			})
		});

		m_username = '';
		m_type = '';
		m_desc = '';

		loadData();
	}

	function logout() {
		localStorage.removeItem('token');
		goto('/');
	}

	onMount(loadData);
</script>

<div class="container" in:fade>

	<header class="header">
		<h1>HIDS Dashboard</h1>
		<button class="logout" onclick={logout}>Logout</button>
	</header>

	<div class="grid">

		<!-- LEFT -->
		<div class="left" in:fly={{ x: -40, duration: 400 }}>

			<div class="card">
				<h3>All Alerts</h3>

				<table>
					<thead>
						<tr>
							<th>ID</th><th>User</th><th>Type</th><th>Description</th><th>Severity</th><th>Time</th>
						</tr>
					</thead>

					<tbody>
						{#each alerts as a}
							<tr>
								<td>{a.id}</td>
								<td>{a.username || '-'}</td>
								<td>{a.alert_type}</td>
								<td>{a.description}</td>
								<td>
									<span class={`badge ${severity(a.alert_type)}`}>
										{severity(a.alert_type).toUpperCase()}
									</span>
								</td>
								<td>{a.timestamp}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

			<div class="card">
				<h3>Login History</h3>

				<table>
					<thead>
						<tr>
							<th>User</th><th>Status</th><th>IP</th><th>Time</th>
						</tr>
					</thead>

					<tbody>
						{#each history as h}
							<tr>
								<td>{h.username}</td>
								<td>{h.status}</td>
								<td>{h.ip_address || '-'}</td>
								<td>{h.timestamp}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>

		</div>

		<!-- RIGHT -->
		<div class="right" in:fly={{ x: 40, duration: 400 }}>

			<div class="card">
				<h3>Alerts Overview</h3>
				<canvas bind:this={chartCanvas}></canvas>
			</div>

			<div class="card">
				<h3>Create Alert</h3>

				<input bind:value={m_username} placeholder="Username" />
				<input bind:value={m_type} placeholder="Type" />
				<textarea bind:value={m_desc} placeholder="Description"></textarea>

				<button onclick={createAlert}>Create Alert</button>
			</div>

		</div>

	</div>

</div>

<style>
    .container {
        padding: 30px;
        background: #0a0f1a;
        min-height: 100vh;
        color: #e5e7eb;
        font-family: Inter, system-ui;
    }
    
    /* HEADER */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
    }
    
    h1 {
        font-size: 20px;
        font-weight: 600;
        color: #60a5fa;
        letter-spacing: 1px;
    }
    
    /* LOGOUT */
    .logout {
        background: transparent;
        border: 1px solid #1e293b;
        color: #94a3b8;
        padding: 6px 12px;
        border-radius: 6px;
        transition: 0.2s;
    }
    
    .logout:hover {
        border-color: #2563eb;
        color: #60a5fa;
    }
    
    /* GRID */
    .grid {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 20px;
    }
    
    /* CARD */
    .card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 0 30px rgba(37,99,235,0.08);
        transition: 0.2s;
    }
    
    .card:hover {
        border-color: rgba(96,165,250,0.3);
    }
    
    /* TABLE */
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }
    
    th, td {
        padding: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    th {
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        font-size: 11px;
    }
    
    tr {
        transition: 0.15s;
    }
    
    tr:hover {
        background: rgba(96,165,250,0.05);
    }
    
    /* BADGES */
    .badge {
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .high {
        background: rgba(239,68,68,0.1);
        color: #f87171;
    }
    
    .medium {
        background: rgba(234,179,8,0.1);
        color: #facc15;
    }
    
    .low {
        background: rgba(34,197,94,0.1);
        color: #4ade80;
    }
    
    /* INPUTS */
    input, textarea {
        width: 100%;
        margin-bottom: 10px;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #1e293b;
        background: #020617;
        color: #e5e7eb;
        font-size: 13px;
    }
    
    input:focus, textarea:focus {
        outline: none;
        border-color: #2563eb;
        box-shadow: 0 0 0 1px #2563eb;
    }
    
    /* BUTTON */
    button {
        width: 100%;
        padding: 10px;
        border-radius: 6px;
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white;
        border: none;
        font-size: 13px;
        transition: 0.2s;
    }
    
    button:hover {
        filter: brightness(1.1);
    }
    
    /* RESPONSIVE */
    @media (max-width: 900px) {
        .grid {
            grid-template-columns: 1fr;
        }
    }
    </style>