<!-- main layout -->

<script lang="ts">
	import {throttle} from 'lodash-es';
	import MemoryUsage from '../components/standalone/MemoryUsage.svelte';
	import GuildsMenu from './GuildsMenu.svelte';

	import { theme, hideSpoilers, font } from './settingsStore';
	import './styles.css';

	import type { PageServerData } from './$types';
	import ContextMenu from 'src/components/menu/ContextMenu.svelte';
	import { position } from 'src/components/menu/menuStore';
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

	function handleMousemove(event) {
		$position = { x: event.clientX, y: event.clientY };
	}
	const handleThrottledMousemove = throttle(handleMousemove, 100, { leading: false, trailing: true });
</script>




<div class="app" on:mousemove={handleThrottledMousemove}>
	<GuildsMenu guilds={data.guilds} selectedGuildId={data.selectedGuildId}/>
	<div class="right">
		<!-- page content on the right -->
		<main>
			<slot />
		</main>
	</div>
</div>
<MemoryUsage />
<ContextMenu />


<style>
	.app {
		display: grid;
		grid-template-columns: 72px 1fr;
		height: 100vh;
		overflow-y: hidden;  /* firefox temp fix */
	}

	.right {
		height: 100%;
	}

	main {
		max-height: 100vh;
		overflow-y: auto;
	}

</style>
