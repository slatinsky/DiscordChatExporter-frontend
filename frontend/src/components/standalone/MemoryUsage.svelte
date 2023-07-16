<script>
	import { onMount, onDestroy } from 'svelte';
	import { developerMode } from 'src/components/settings/settingsStore';

	let memoryInterval;
	let objectsCount = 0;
	let memoryUsage = {};
	onMount(() => {
		if (window?.performance?.memory?.usedJSHeapSize) {
			memoryInterval = setInterval(() => {
				memoryUsage = window.performance.memory;
				objectsCount = document.getElementsByTagName('*').length;
			}, 1000);
		}
	});

	onDestroy(() => {
		clearInterval(memoryInterval);
	});
</script>

{#if $developerMode && 'usedJSHeapSize' in memoryUsage}
	<div id="memory-usage">
		Memory used {Math.round(memoryUsage.usedJSHeapSize / 1024 / 1024)} MB / {Math.round(
			memoryUsage.jsHeapSizeLimit / 1024 / 1024
		)} MB ({Math.round((memoryUsage.usedJSHeapSize / memoryUsage.jsHeapSizeLimit) * 100)}%),
		DOM objects: {objectsCount}
	</div>
{/if}


<style>
#memory-usage {
	position: fixed;
	bottom: 0;
	right: 10px;
	background-color: #00000088;
	padding: 5px 10px;
	border-radius: 5px;
	color: var(--text-secondary);
	font-size: 12px;
	pointer-events: none;
}
</style>