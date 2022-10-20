<script>
	import MessageGroup from './MessageGroup.svelte';
	export let messages;
	export let guild;
	export let channelId;
	export let search = false

	// }

	// console.error('messages-----',  Object.keys(messages)[0]);


</script>



<!-- {#key channelId} -->
	{#if messages}
		<MessageGroup messages={messages} splitMessages={Object.values(messages)} {guild} {search}></MessageGroup>
	{:else}
		<div class="no-messages">No messages</div>
	{/if}
<!-- {/key} -->


<style>
	.no-messages {
		padding-left: 46px;
	}
</style>
