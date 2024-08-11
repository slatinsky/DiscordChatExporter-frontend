<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	let mainContainer: HTMLElement;

	function removeSpoiler(e: MouseEvent) {
		console.log(e.target);
		// handle spoilers globally in containers
		if (e.target && e.target.matches(".d-spoiler")) {
			e.target.classList.remove("d-spoiler");
			e.target.classList.add("d-spoiler-revealed");
		}
		if (e.target && e.target.matches(".media-spoiler")) {
			e.target.classList.remove("media-spoiler");
			e.target.classList.add("media-spoiler-revealed");
		}
	}

	onMount(() => {
		console.log();
		mainContainer.addEventListener("click", removeSpoiler);
	})

	onDestroy(() => {
		mainContainer?.removeEventListener("click", removeSpoiler);
	})
</script>



<div bind:this={mainContainer}>
	<slot />
</div>

<style>
	:global([data-hidespoilers="true"] .d-spoiler) {
		background-color: rgba(0, 0, 0, 0.3);
		color: transparent !important;
		border-radius: 3px;
		-webkit-backdrop-filter: blur(10px);
		backdrop-filter: blur(10px);
		cursor: pointer;
	}
	:global([data-hidespoilers="true"] .d-spoiler > *) {
		pointer-events:none;
	}
	:global([data-hidespoilers="true"] .d-spoiler img) {
		visibility: hidden;
	}
	:global([data-hidespoilers="true"] .d-spoiler a) {
		color: transparent !important;
	}

	:global(.d-spoiler-revealed),
	:global([data-hidespoilers="false"] .d-spoiler) {
		background-color: rgba(0, 0, 0, 0.3);
	}

	:global([data-hidespoilers="true"] .media-spoiler) {
		filter: blur(100px);
		cursor: pointer;
	}
	:global([data-hidespoilers="true"] .media-spoiler > *) {
		pointer-events:none;
	}
</style>