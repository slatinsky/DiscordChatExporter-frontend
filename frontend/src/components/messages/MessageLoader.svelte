<script>
	import { onDestroy, onMount } from "svelte";
	import { cancelMessageContentRequest, getMessageContent } from "../../js/messageMiddleware";
	import NewMessage from "./NewMessage.svelte";
	export let messageId = null;
	export let previousMessageId = null;
	export let selectedGuildId = null;

	// fetch message from api
	let messagePromise = getMessageContent(messageId);
	let previousMessagePromise
	let fullMessagePromise

	if (previousMessageId !== null) {
		previousMessagePromise = getMessageContent(previousMessageId);
		fullMessagePromise = Promise.all([messagePromise, previousMessagePromise]);
	} else {
		fullMessagePromise = Promise.all([messagePromise]);
	}


	onDestroy(() => {
		cancelMessageContentRequest(messageId);
	});

</script>

{#if messageId}
	{#await fullMessagePromise}
		<div class="loading">Loading... {messageId}</div>
	{:then messages}
		{#key message._id}
			<NewMessage message={messages[0]} previousMessage={messages[1]} {selectedGuildId}/>
		{/key}
		<!-- <p>{message.content[0].content}</p> -->
	{:catch error}
		<div style="color: red" class="loading">{error} <span class="retry-btn" on:click={() => messagePromise = getMessageContent(messageId)}>retry</span></div>
	{/await}
{/if}

<style>
	.loading {
		height: 100px;
		color: gray;
	}
	.retry-btn {
		color: white;
		cursor: pointer;
		background-color: black;
		padding: 2.5px 5px;
	}
</style>