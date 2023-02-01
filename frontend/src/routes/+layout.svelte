<!-- main layout -->

<script lang="ts">
	import MemoryUsage from '../components/standalone/MemoryUsage.svelte';
	import GuildsMenu from './GuildsMenu.svelte';

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




<div class="app">
	<GuildsMenu guilds={data.guilds} selectedGuildId={data.selectedGuildId}/>
	<div class="right">
		<!-- page content on the right -->
		<main>
			<slot />
		</main>
	</div>
</div>
<MemoryUsage />


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
