<script>
	import { onDestroy, onMount } from "svelte";
	import { cancelMessageContentRequest, getMessageContent } from "../../../../js/messageMiddleware";
	import NewMessage from "./NewMessage.svelte";
	export let messageId = null;
	export let selectedGuildId = null;

	// fetch message from api
	let messagePromise = getMessageContent(messageId);

	onDestroy(() => {
		cancelMessageContentRequest(messageId);
	});

</script>

{#if messageId}
	{#await messagePromise}
		<div class="loading">Loading... {messageId}</div>
	{:then message}
		{#key message._id}
			<NewMessage {message} {selectedGuildId}/>
		{/key}
		<!-- <p>{message.content[0].content}</p> -->
	{:catch error}
		<p style="color: red" class="loading">{error}</p>
	{/await}
{/if}

<style>
	.loading {
		height: 100px;
		color: gray;
	}
</style>