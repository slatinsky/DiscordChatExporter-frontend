<script>
	import { onDestroy, onMount } from 'svelte';
	import MessageGroup from './MessageGroup.svelte';
	export let messages;
	export let guild;
	export let channelId;
	export let search = false
	export let rootId

	let mainContainer;

	function removeSpoiler(e) {
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
	{#key channelId}
		{#if messages}
			<MessageGroup messages={messages} splitMessages={messages} {guild} {search} {rootId}></MessageGroup>
		{:else}
			<div class="no-messages">No messages</div>
		{/if}
	{/key}
</div>


<style>
	.no-messages {
		padding-left: 46px;
	}
</style>
