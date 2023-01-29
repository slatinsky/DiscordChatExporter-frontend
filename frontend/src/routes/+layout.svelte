<!-- main layout -->

<script lang="ts">
	import MemoryUsage from '../components/standalone/MemoryUsage.svelte';
	import GuildsMenu from './GuildsMenu.svelte';
	import ContainerCenter from 'src/components/containers/ContainerCenter.svelte';

	import { theme, hideSpoilers, font } from './settingsStore';
	import './styles.css';

	import type { PageServerData } from './$types';
	export let data: PageServerData;

	theme.subscribe(value => {
		document.documentElement.setAttribute('data-theme', value);
	});

	hideSpoilers.subscribe(value => {
		document.documentElement.setAttribute('data-hidespoilers', value);
	});

	font.subscribe(value => {
		document.documentElement.setAttribute('data-font', value);
	});
</script>



{#if Object.values(data.guilds).length === 0}
	<ContainerCenter>
		<h1>No chat exports found</h1>
		<p>
			Please close this app and "nginx" window, move your DiscordChatExporter JSON+media exports to "/exports/" folder and rerun
			"START_VIEWER.bat"
		</p>

		<small>If your exports are in the correct place and you still see this error, please open an issue on <a href="https://github.com/slatinsky/DiscordChatExporter-frontend/issues" target="_blank">GitHub</a>. Please check out command line window if you see any errors / crashes there</small>
	</ContainerCenter>
{:else}
	<div class="app">
		<GuildsMenu guilds={data.guilds}/>
		<div class="right">
			<!-- page content on the right -->
			<main>
				<slot />
			</main>
		</div>
	</div>
	<MemoryUsage />
{/if}

<style>
	.app {
		display: grid;
		grid-template-columns: 70px 1fr;
		height: 100vh;
	}

	.right {
		height: 100%;
	}

</style>
