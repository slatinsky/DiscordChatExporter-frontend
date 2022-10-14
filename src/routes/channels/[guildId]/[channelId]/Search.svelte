<script>
	import { onMount } from "svelte";
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

	/**
	 * Because messages are wrapped in message groups for performance reasons,
	 * we need to find recursivelly the message group that contains the message we want to scroll to.
	 */
	function searchForMessageId(messageId, recursionDepth = 0) {
		if (recursionDepth > 100) {
			console.error('recursion depth exceeded');
			return;
		}
		let elMessage = document.getElementById(messageId);
		if (elMessage) {
			elMessage.scrollIntoView();
			console.log('found message', messageId, "- recursion depth", recursionDepth);
			return;
		}

		let visibleMessageIds = []
		for (const mg of document.querySelectorAll('.message-group')) {
			visibleMessageIds.push([BigInt(mg.dataset.mgfirst), BigInt(mg.dataset.mglast)]);
		}

		// console.log('visibleMessageIds', visibleMessageIds);

		let bestRange = null;
		let bestError = BigInt("999999999999999999999999999999")

		for (let i = 0; i < visibleMessageIds.length; i++) {
			let first = BigInt(visibleMessageIds[i][0]);
			let last = BigInt(visibleMessageIds[i][1]);
			let currentError = last - first;  // we want to find the smallest message group that contains the message we want to scroll to
			if (messageId >= first && messageId <= last && currentError < bestError) {
				bestError = currentError;
				bestRange = [first,last];
				// console.log('found message in visible range', messageId, first, last, bestError);
			}
		}

		if (bestRange) {
			let first = bestRange[0];
			let last = bestRange[1];
			let el = document.querySelector('.message-group[data-mgfirst="' + first + '"][data-mglast="' + last + '"]')
				if (el) {
					el.scrollIntoView();
					setTimeout(() => {
						searchForMessageId(messageId, recursionDepth+1)
					}, 1);
				}
				else {
					console.log('could not find message group with id', closestMessageId);
				}
				return;
		} else {
			console.log('message not found', messageId);
		}




	}

	function addHashToUrl(messages, searchTerm, messageId) {
		searchForMessageId(BigInt(messageId))
		window.location.hash = messageId;
		// console.log('added hash to url', window.location.hash, elSearchInput);

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

	onMount(() => {
		// if hash is present in url, search for it
		if (window.location.hash) {
			let messageId = window.location.hash.replace('#', '');
			searchForMessageId(BigInt(messageId));
		}
		else {
			// scroll to top
			document.querySelector('#top').scrollIntoView();
		}
	});

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
