<script>
	import { onMount, onDestroy } from 'svelte';
	import Message from './Message.svelte';

	export let messages;
	export let splitMessages;
	export let guild;
	export let search = false
	export let rootId

	let messageCount = splitMessages.length;
	let createGroup = messageCount > 16;

	let firstHalfMessages;
	let secondHalfMessages;
	let loaded = false;
	let root;
	let observer;
	let firstMessageId;
	let lastMessageId;

	if (createGroup) {
		firstMessageId = splitMessages[0].id;
		lastMessageId = splitMessages[splitMessages.length - 1].id;
		firstHalfMessages = splitMessages.slice(0, messageCount / 2);
		secondHalfMessages = splitMessages.slice(messageCount / 2, messageCount);
		observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting) {
						console.log('loaded message group with size', messageCount);
						observer.disconnect();

						loaded = true;
					}
				});
			},
			{
				root: rootId,
				rootMargin: '500% 0px',
			}
		);
	}


	onMount(() => {
		if (createGroup) {
			observer.observe(root);
		}
	});

	onDestroy(() => {
		if (observer) {
			observer.disconnect();
		}
	});
</script>

{#if createGroup}
	<div
		bind:this={root}
		class={search ? undefined : "message-group"}
		data-mgfirst={search ? undefined : firstMessageId}
		data-mglast={search ? undefined : lastMessageId}
	>
		{#if loaded}
			<svelte:self {messages} splitMessages={firstHalfMessages} {guild} {search} {rootId}/>
			<svelte:self {messages} splitMessages={secondHalfMessages} {guild} {search} {rootId}/>
		{:else}
			<div class="not-loaded" style="height: {messageCount * 50}px;width: 100%;" />
		{/if}
	</div>
{:else}
	<div>
		{#each splitMessages as message (message['id'])}
			<!-- skip thread start msg -->
			{#if message.type !== '21'}
				<Message {message} {guild} {search} {rootId}/>
			{/if}
		{/each}
	</div>
{/if}
