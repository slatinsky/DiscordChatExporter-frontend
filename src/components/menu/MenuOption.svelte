<script>
	import { onMount, getContext } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import { isMenuVisible } from './menuStore';
	const key = {};

	export let text = '';
	export let visible;

	const dispatch = createEventDispatcher();

	// const { dispatchClick } = getContext(key);

	const handleClick = e => {
        dispatch('click');
        visible.set(false);
	}
</script>

<style>
	div {
		padding: 10px 20px;
		cursor: default;
		font-size: 14px;
		display: flex;
		align-items: center;
		grid-gap: 5px;
        color: #787A7E   ;
	}
	div:hover {
		background: #4752C4;
        color: white;
	}
	/* div.disabled {
		color: #0006;
	}
	div.disabled:hover {
		background: white;
	} */
</style>

<div on:click={handleClick} class="menu-option">
	{#if text}
		{text}
	{:else}
		<slot />
	{/if}
</div>
