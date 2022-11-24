<script>
	import { writable } from 'svelte/store';
	import Menu from './Menu.svelte';

	export let visible = writable(true);

	async function onRightClick(e) {
		if ($visible) {
			$visible = false;
			await new Promise(res => setTimeout(res, 100));
		}
		$visible = true;
	}

	function closeMenu() {
		$visible = false;
	}
</script>

{#if $visible}
	<Menu on:click={closeMenu} on:clickoutside={closeMenu} {visible}>
		<slot />
	</Menu>
{/if}
