<script>
	import Message from "./Message.svelte";
	export let messageId = null;
	
	// fetch message from api
	async function fetchMessage(messageId) {
		try {
			let res = await fetch(`/api/messages/${messageId}`)
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
		<div class="loading">Loading... {messagePromise._id}</div>
	{:then message}
		<!-- <Message {message}/> -->
		<p>{message.content[0].content}</p>
	{/await}
{/if}