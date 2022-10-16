<script>
    import Messages from './[channelId]/Messages.svelte';
    export let searched = false;
    export let found_messages = [];
    export let guild
</script>

{#key found_messages}
	{#if searched}
		<div class="search-found-count">
			<div>{found_messages.length} Results</div>
			<button on:click={()=>searched=false}>×</button>
		</div>
	{/if}
	<div class="search-results">
		<Messages messages={found_messages} {guild} channelId={0} search={true} />
	</div>
{/key}

<style>
    .search-results {
		overflow-y: auto;
		overflow-x: hidden;
		max-height: calc(100vh - 96px);
		margin-right: 5px;
		width: 100%;

		background-color: #2F3136;
	}
	.search-found-count {
		background-color: #202225;
		padding: 15px 30px;

		display: flex;
		justify-content: space-between;
	}
</style>