<script>
	import { found_messages, searched } from './searchStores';
    import Messages from './[channelId]/Messages.svelte';
    export let guild
	let searchResults
</script>

{#if $searched}
	<div class="search-found-count">
		<div>{$found_messages.length} Results</div>
		<button on:click={()=>$searched=false} class="search-dismiss-btn">×</button>
	</div>
{/if}
<div id="search-results" bind:this={searchResults}>
	{#if searchResults}
		<Messages messages={$found_messages} {guild} channelId={$found_messages} search={true} rootId={searchResults}/>
	{/if}
</div>

<style>
    #search-results {
		overflow-y: auto;
		overflow-x: hidden;
		max-height: calc(100vh - 104px);
		margin-right: 5px;
		width: 100%;

		background-color: #2F3136;
	}
	.search-found-count {
		background-color: #202225;
		padding: 15px 30px;

		display: flex;
		justify-content: space-between;

		position: relative;
	}

	.search-dismiss-btn {
		background-color: transparent;
		border: none;
		color: #DCDDDE;
		font-size: 3rem;
		font-weight: 600;
		cursor: pointer;
		position:absolute;
		top: -6px;
		right: 15px;
	}
</style>