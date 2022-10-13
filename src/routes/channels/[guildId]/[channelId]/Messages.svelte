<script>
	import { copyTextToClipboard } from '../../../../helpers';
	import { onlyMatches, foundMessageIds, searchTerm } from './searchStore';
	import VirtualList from 'svelte-tiny-virtual-list';
	import Message from './Message.svelte';
	export let messages;
	export let authors;
	export let emojis;

	export let guildId;

	// let page = 0;
	// let pageSize = 10000;
	// $: pages = Math.ceil(messages.length / pageSize);
	// $: pageMessages = messages.slice(page * pageSize, (page + 1) * pageSize);

	// $: console.log('pageMessages.length', pageMessages.length);

	// function prevPage() {
	// 	if (page > 0) {
	// 		page--;
	// 	}
	// 	window.location.hash = '';
	// 	setTimeout(() => {
	// 		window.location.hash = 'bottom';
	// 	}, 0);
	// }

	// function nextPage() {
	// 	if (page < pages - 1) {
	// 		page++;
	// 	}
	// 	window.location.hash = '';
	// 	setTimeout(() => {
	// 		window.location.hash = 'top';
	// 	}, 0);
	// }

	// function messagesChanged(messages) {
	// 	setTimeout(() => {
	// 		// page = pages - 1;
	// 		page = 0;
	// 	}, 0);
	// }

	console.error('messages-----',  Object.keys(messages)[0]);





	// $: console.log('mmmm', pageMessages);
	// $: messagesChanged(messages);

	// $: pageMessages = addAuthorsToMessages(pageMessages, authors);
	// $: pageMessages = addEmojisToMessages(pageMessages, emojis);
	// $: pageMessages = addReferencedMessages(pageMessages);
	// $: console.log('authors', authors);
	// $: console.log('messages', messages);
</script>

<div id="top" />
<!-- <div class="pagination">
	{#if pages > 1}
		<button on:click={prevPage} disabled={page == 0}>PREV PAGE</button>
	{/if}
	<div>Page {page + 1} of {pages}</div>
	{#if pages > 1}
		<button on:click={nextPage} disabled={page == pages-1}>NEXT PAGE</button>
	{/if}
</div> -->

<!-- <VirtualList
    width="100%"
    height="600px"
    itemCount={pageMessages.length}
    itemSize={150}>
  <div slot="item" let:index let:style {style}>
	<Message message={pageMessages[index]} {messages} {authors} {emojis} />
  </div>
</VirtualList> -->

{#each Object.values(messages) as message}
	<Message message={message} messages={messages} {authors} {emojis} {guildId} />

	<!-- <p>{pageMessages[index].content} {pageMessages[index].author}</p> -->
	<!-- {#if !$onlyMatches || $searchTerm == '' || $foundMessageIds.includes(pageMessages[index].id)}
		
	{/if} -->
	<!-- <pre>{JSON.stringify(message, null, 2)}</pre> -->
{/each}
<div id="bottom" />

<style>
	/* .pagination {
		position: fixed;
		display: flex;
		align-items: center;
		gap: 10px;

		background-color: #202225;
		width: 100%;

		padding: 17px;
		margin-top: -67px;

		z-index: 100;
	} */

	#top {
		/* padding-bottom: 50px; */
	}
</style>
