<script>
	import { onlyMatches, searchTerm, foundMessageIds } from "./searchStore";

	export let messages;

	let resultsCount = 0;
	let resultsIndex = 0;

	// dom elements
	let elSearchInput;

	// let onlyMatches = false;

	function removeAccents(str) {
		return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
	}

	function normalizeSearchTerm(str) {
		return removeAccents(str.toLowerCase());
	}

    function newMessages(messages) {
        resultsIndex = 0
    }

    $: newMessages(messages)

	function searchMessages(messages, searchTerm, resultsIndex) {
        if (searchTerm === '') {
            $foundMessageIds = [];
            resultsCount = Object.keys(messages).length;
            return;
        }
		console.log('searching for', searchTerm);
		let searchResults = [];
		for (let message of Object.values(messages)) {
			if (normalizeSearchTerm(message.content).includes(normalizeSearchTerm(searchTerm))) {
				searchResults.push(message.id);
			}
		}
		resultsCount = searchResults.length;
        $foundMessageIds = searchResults;

		addHashToUrl(messages, searchTerm, searchResults[resultsIndex]);
		return searchResults;
	}

	function addHashToUrl(messages, searchTerm, messageId) {
		window.location.hash = messageId;
		console.log('added hash to url', window.location.hash, elSearchInput);

		if (elSearchInput) {
			elSearchInput.focus();
		}
	}

	function prev() {
		if (resultsIndex > 0) {
			resultsIndex--;
			// scrollToMessage(searchResults[resultsIndex]);
		}
	}

	function next() {
		if (resultsIndex < resultsCount - 1) {
			resultsIndex++;
			// scrollToMessage(searchResults[resultsIndex]);
		}
	}

	$: searchResults = searchMessages(messages, $searchTerm, resultsIndex);
</script>

<input
	type="text"
	placeholder="search"
	id="search-input"
	class={resultsCount == 0 ? 'not-found' : ''}
	bind:value={$searchTerm}
	bind:this={elSearchInput}
/>
{#if resultsCount == 0}
	<div class="search-results-count not-found-txt">No results</div>
{:else if $searchTerm}
	<div class="search-results-count">Showing result {resultsIndex + 1} / {resultsCount}</div>
	<button on:click={prev}>Prev</button>
	<button on:click={next}>Next</button>
	<label>
		<input type="checkbox" id="show-only-matches" bind:checked={$onlyMatches} />
        show only matches
	</label>
{:else}
	<div>{resultsCount} messages</div>
{/if}

<style>
	.not-found {
		background-color: red;
	}

	.not-found-txt {
		color: red;
	}
</style>
