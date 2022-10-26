<script>
	import { onMount, setContext, createEventDispatcher } from 'svelte';
	import { fade } from 'svelte/transition';
	import { position } from './menuStore';
	const key = {};
    export let visible

    $: x = $position.x;
    $: y = $position.y;

	// whenever x and y is changed, restrict box to be within bounds
	$: (() => {
		if (!menuEl) return;

		const rect = menuEl.getBoundingClientRect();
		x = Math.min(window.innerWidth - rect.width, x);
		if (y > window.innerHeight - rect.height) y -= rect.height;
	})(x, y);

	const dispatch = createEventDispatcher();

	setContext(key, {
		dispatchClick: () => dispatch('click')
	});

	let menuEl;
	function onPageClick(e) {
        if (e.target.classList.contains("menu-option")) {
            $visible = false;
        }
        else {
            $visible = true;
		    dispatch('clickoutside');
        }
	}

    // $: console.log("isRightClickMenuVisible", $visible);
</script>

<style>
	div {
		position: absolute;
		display: grid;
		border: 1px solid #0003;
		box-shadow: 2px 2px 5px 0px #0002;
		background: #18191C;
	}
</style>

<svelte:body on:click={onPageClick} />

{#if $visible}
    <div transition:fade={{ duration: 100 }} bind:this={menuEl} style="top: {y}px; left: {x}px;">
        <slot />
    </div>
{/if}