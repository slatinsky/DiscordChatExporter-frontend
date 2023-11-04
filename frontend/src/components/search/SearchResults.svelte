<script lang="ts">
	import MesssageSpoilerHandler from '../messages/MesssageSpoilerHandler.svelte';
	import Scroller from '../containers/Scroller3.svelte';
	import { doSearch, isSearching, searchPrompt, searchResultsMessageIds, searchShown, submitSearch } from './searchStores';
	import MessageLoader from '../messages/MessageLoader.svelte';
	let searchResults
	export let guildId: string

	let reversed = false

	$: orderedSearchResultsMessageIds = reversed ? $searchResultsMessageIds.slice().reverse() : $searchResultsMessageIds

	/**
	 * 797196 -> 797,196
	 */
	function addNumberDelimeter(number: number) {
		return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
	}

	function showAllResults() {
		if ($searchPrompt.includes('limit:')) {
			doSearch($searchPrompt.replace(/limit:\d+/, 'limit:0'), guildId)
		} else {
			doSearch('limit:0 ' + $searchPrompt, guildId)
		}
	}
</script>

<div class="search-found-count">
	{#if $isSearching}
		<div>Searching...</div>
	{:else}
		<div style="text-align: center;">
			<span>{addNumberDelimeter($searchResultsMessageIds.length)} Results</span>
			{#if orderedSearchResultsMessageIds.length == 100000}
				<button class="btn-limit-0" on:click={showAllResults}>Show all</button>
			{/if}
		</div>
		<div>
			<button class="search-result-order-btn" class:active={reversed == false} on:click={() => reversed = false}>New</button>
			<button class="search-result-order-btn" class:active={reversed == true} on:click={() => reversed = true}>Old</button>
		</div>
	{/if}
</div>
<div id="search-results" bind:this={searchResults}>
	<div style="width: 100%;"></div>
	{#if searchResults && !$isSearching}
		<MesssageSpoilerHandler>
			{#key orderedSearchResultsMessageIds}
			<Scroller
				itemCount={orderedSearchResultsMessageIds.length}
				negativeHeight={110}
				>
				<div slot="item" let:index>
					<MessageLoader messageId={orderedSearchResultsMessageIds[index]} previousMessageId={orderedSearchResultsMessageIds[index - 1]} selectedGuildId={guildId}/>
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
		background-color: #1E1F22;
		padding: 15px 30px;

		display: flex;
		justify-content: space-between;

		position: relative;
		align-items: center;
	}

	.search-result-order-btn {
		margin-left: 6px;
		margin-bottom: 2px;
		border-radius: 4px;
		padding: 6px 10px;
		color: #B5BAC1;
		background-color: #1E1F22;
		border: none;
		font-size: 16px;
		line-height: 20px;
		cursor: pointer;
		font-weight: 500;
	}
	.search-result-order-btn:hover {
		color: #DBDEE1;
		background-color: #2C2E32;
	}

	.search-result-order-btn.active {
		color: white;
		background-color: #3B3C43;
	}
	.search-result-order-btn.active:hover {
		background-color: #2C2E32;
	}

	.btn-limit-0 {
		font-size: 12px;
		margin-left: 6px;

		border-radius: 4px;
		padding: 6px 10px;
		color: #B5BAC1;
		background-color: #323438;
		border: none;
		line-height: 20px;
		cursor: pointer;
		font-weight: 500;
	}
</style>