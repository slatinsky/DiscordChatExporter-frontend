<script lang="ts">
	import { getMessageContent } from "../../js/messageMiddleware";
	import NewMessage from "./NewMessage.svelte";
	export let messageId: string;
	export let previousMessageId: string | null  = null;
	export let selectedGuildId: string;
	export let guildName: string;

	// fetch message from api
	async function fetchMessages(messageId: string, previousMessageId: string | null, selectedGuildId: string) {
		const messagePromise = getMessageContent(messageId, selectedGuildId);
		let previousMessage
		if (previousMessageId !== null) {
			previousMessage = await getMessageContent(previousMessageId, selectedGuildId);
		}
		else {
			previousMessage = null;
		}

		const message = await messagePromise;

		let referencedMessage

		if (message.reference) {
			referencedMessage = message.reference.message
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
	let fullMessagesPromise = fetchMessages(messageId, previousMessageId, selectedGuildId);
</script>
{#if messageId == "error"}
	<div class="search-error">SEARCH ERROR - check server logs for details</div>
{:else if messageId}
	{#await fullMessagesPromise}
		<div class="loading">Loading... {messageId}</div>
	{:then messages}
		{#key messages}
			<NewMessage message={messages.message} previousMessage={messages.previousMessage} referencedMessage={messages.referencedMessage} {selectedGuildId} {guildName}/>
		{/key}
	{:catch error}
		<div style="color: red" class="loading">{error} <span class="retry-btn" on:click={() => fullMessagesPromise = fetchMessages(messageId, previousMessageId, selectedGuildId)}>retry</span></div>
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