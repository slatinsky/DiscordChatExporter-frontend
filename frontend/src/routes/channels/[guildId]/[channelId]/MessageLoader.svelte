<script>
	import NewMessage from "./NewMessage.svelte";
	export let messageId = null;
	export let selectedGuildId = null;

	// fetch message from api
	async function fetchMessage(messageId) {
		try {
			let res = await fetch(`/api/message?message_id=${messageId}`)
			let json = await res.json();
			console.log(json);
			return json;
		}
		catch (err) {
			console.error(err);
		}
	}
	let messagePromise = fetchMessage(messageId);

</script>

{#if messageId}
	{#await messagePromise}
		<div class="loading">Loading... {messageId}</div>
	{:then message}
		{#key message._id}
			<NewMessage {message} {selectedGuildId}/>
		{/key}
		<!-- <p>{message.content[0].content}</p> -->
	{/await}
{/if}

<style>
	.loading {
		height: 50px;
		color: gray;
	}
</style>