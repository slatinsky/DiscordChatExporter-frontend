<script lang="ts">
	import { getMessageContent } from "../../js/messageMiddleware";
	import NewMessage from "./NewMessage.svelte";
	export let messageId: string;
	export let previousMessageId: string | null  = null;
	export let selectedGuildId: string;

	// fetch message from api
	async function fetchMessages(messageId: string, previousMessageId: string | null) {
		const messagePromise = getMessageContent(messageId);
		let previousMessage
		if (previousMessageId !== null) {
			previousMessage = await getMessageContent(previousMessageId);
		}
		else {
			previousMessage = null;
		}

		const message = await messagePromise;

		let referencedMessage

		if (message.reference) {
			referencedMessage = await getMessageContent(message.reference.messageId);
		}
		else {
			referencedMessage = null;
		}

		return {
			message: message,
			previousMessage: previousMessage,
			referencedMessage: referencedMessage
		}
	}

	// promise
	let fullMessagesPromise = fetchMessages(messageId, previousMessageId);
</script>
{#if messageId == "error"}
	<div class="search-error">SEARCH ERROR - check server logs for details</div>
{:else if messageId}
	{#await fullMessagesPromise}
		<div class="loading">Loading... {messageId}</div>
	{:then messages}
		{#key messages}
			<NewMessage message={messages.message} previousMessage={messages.previousMessage} referencedMessage={messages.referencedMessage} {selectedGuildId}/>
		{/key}
	{:catch error}
		<div style="color: red" class="loading">{error} <span class="retry-btn" on:click={() => fullMessagesPromise = fetchMessages(messageId, previousMessageId)}>retry</span></div>
	{/await}
{/if}

<style>
	.loading {
		height: 100px;
		color: gray;
		padding-left: 2rem;
	}
	.retry-btn {
		color: white;
		cursor: pointer;
		background-color: black;
		padding: 2.5px 5px;
	}

	.search-error {
		color: red;
		padding: 1rem 2rem;
	}
</style>