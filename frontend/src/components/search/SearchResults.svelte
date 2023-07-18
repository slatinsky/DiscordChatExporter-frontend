<script lang="ts">
	import MesssageSpoilerHandler from '../messages/MesssageSpoilerHandler.svelte';
	import Scroller from '../containers/Scroller3.svelte';
	import { searchResultsMessageIds, searchShown } from './searchStores';
	import MessageLoader from '../messages/MessageLoader.svelte';
	let searchResults
	export let guildId: string
</script>

{#if $searchShown}
	<div class="search-found-count">
		<div>{$searchResultsMessageIds.length} Results</div>
	</div>
{/if}
<div id="search-results" bind:this={searchResults}>
	{#if searchResults}
	<MesssageSpoilerHandler>
		{#key $searchResultsMessageIds}
		<Scroller
			itemCount={$searchResultsMessageIds.length}
			negativeHeight={110}
			>
			<div slot="item" let:index>
				<MessageLoader messageId={$searchResultsMessageIds[index]} previousMessageId={$searchResultsMessageIds[index - 1]} selectedGuildId={guildId}/>
			</div>
		</Scroller>
		{/key}
	</MesssageSpoilerHandler>
	{/if}
</div>

<style>
    #search-results {
		overflow-y: auto;
		overflow-x: hidden;
		max-height: calc(100vh - 104px);
		margin-right: 5px;
		width: 100%;

		background-color: #2b2d31;
	}
	.search-found-count {
		background-color: #202225;
		padding: 15px 30px;

		display: flex;
		justify-content: space-between;

		position: relative;
	}
</style>