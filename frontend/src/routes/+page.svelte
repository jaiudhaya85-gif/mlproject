<svelte:head>
	<title>HIDS | {mode === 'login' ? 'Login' : 'Register'}</title>
</svelte:head>
<script lang="ts">
	import { goto } from '$app/navigation';
	import { fade, fly } from 'svelte/transition';

	const baseURL = 'http://127.0.0.1:5000';

	let mode = $state<'login' | 'register'>('login');

	let username = $state('');
	let password = $state('');
	let message = $state<string | null>(null);
	let loading = $state(false);
    let showPassword = $state(false);
	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		loading = true;
		message = null;

		const endpoint = mode === 'login' ? '/login' : '/register';

		try {
			const res = await fetch(`${baseURL}${endpoint}`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			});

			const data = await res.json();

			if (mode === 'login' && res.ok && data.token) {
				localStorage.setItem('token', data.token);
				goto('/dashboard');
			} else {
				message = data.msg || 'Authentication failed';
			}
		} catch {
			message = 'Network error';
		} finally {
			loading = false;
		}
	}
</script>

<div class="auth" in:fade>

	<!-- Background grid -->
	<div class="grid-bg"></div>

	<div class="panel" in:fly={{ y: 30, duration: 400 }}>

		<div class="header">
			<h1>HIDS</h1>
			<p>Host Intrusion Detection System</p>
		</div>

		<h2>{mode === 'login' ? 'Access Console' : 'Register Node'}</h2>

		<form onsubmit={handleSubmit} class="form">

			<input
				bind:value={username}
				placeholder="username"
				required
			/>

			<input
				type="password"
				bind:value={password}
				placeholder="password"
				required
			/>

			<button disabled={loading}>
				{loading ? 'Processing...' : mode === 'login' ? 'Enter System' : 'Create Access'}
			</button>

		</form>

		<div class="switch">
			{mode === 'login'
				? 'No access?'
				: 'Already authenticated?'}
			<button onclick={() => (mode = mode === 'login' ? 'register' : 'login')}>
				{mode === 'login' ? 'Request Access' : 'Login'}
			</button>
		</div>

		{#if message}
			<div class="error">{message}</div>
		{/if}

	</div>
</div>

<style>
.auth {
	position: relative;
	height: 100vh;
	display: flex;
	justify-content: center;
	align-items: center;
	background: #0a0f1a;
	color: #e5e7eb;
	font-family: "Inter", system-ui;
}

/* subtle grid background */
.grid-bg {
	position: absolute;
	width: 100%;
	height: 100%;
	background-image:
		linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
		linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
	background-size: 40px 40px;
}

/* main panel */
.panel {
	position: relative;
	background: rgba(15, 23, 42, 0.85);
	border: 1px solid rgba(255,255,255,0.08);
	backdrop-filter: blur(10px);
	padding: 30px;
	width: 320px;
	border-radius: 12px;
	box-shadow: 0 0 40px rgba(37, 99, 235, 0.1);
}

/* header */
.header h1 {
	margin: 0;
	font-size: 20px;
	font-weight: 600;
	letter-spacing: 1px;
	color: #60a5fa;
}

.header p {
	font-size: 11px;
	color: #6b7280;
	margin-bottom: 20px;
}

h2 {
	font-size: 16px;
	margin-bottom: 16px;
}

/* form */
.form {
	display: flex;
	flex-direction: column;
	gap: 10px;
}

input {
	background: #020617;
	border: 1px solid #1e293b;
	color: #e5e7eb;
	padding: 10px;
	border-radius: 6px;
	font-size: 13px;
}

input:focus {
	outline: none;
	border-color: #2563eb;
	box-shadow: 0 0 0 1px #2563eb;
}

/* button */
button {
	background: linear-gradient(90deg, #2563eb, #1d4ed8);
	border: none;
	padding: 10px;
	border-radius: 6px;
	color: white;
	font-weight: 500;
	cursor: pointer;
	transition: 0.2s;
}

button:hover {
	filter: brightness(1.1);
}

/* switch */
.switch {
	margin-top: 12px;
	font-size: 12px;
	color: #6b7280;
}

.switch button {
	background: none;
	color: #60a5fa;
	border: none;
	cursor: pointer;
	margin-left: 6px;
}

/* error */
.error {
	margin-top: 10px;
	padding: 8px;
	background: rgba(239, 68, 68, 0.1);
	color: #f87171;
	border: 1px solid rgba(239, 68, 68, 0.2);
	border-radius: 6px;
	font-size: 12px;
}
</style>