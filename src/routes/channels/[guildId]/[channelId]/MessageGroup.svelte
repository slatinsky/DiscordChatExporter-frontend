<script>
	import { onMount, onDestroy } from 'svelte';
	import Message from './Message.svelte';

	export let messages;
	export let splitMessages;
	export let guild;
	export let guildId;
	export let search = false

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
				rootMargin: '100% 0px 100% 0px'
			}
		);
	}

	onMount(() => {
		// console.log('onMount');
		if (createGroup) {
			observer.observe(root);
		}
	});

	onDestroy(() => {
		// console.log('onDestroy');
		if (createGroup) {
			observer.disconnect();
		}
	});
</script>

{#if createGroup}
	<div
		bind:this={root}
		class="message-group"
		data-mgfirst={firstMessageId}
		data-mglast={lastMessageId}
	>
		{#if loaded}
			<svelte:self {messages} splitMessages={firstHalfMessages} {guild} {guildId} {search}/>
			<svelte:self {messages} splitMessages={secondHalfMessages} {guild} {guildId} {search}/>
		{:else}
			<div class="not-loaded" style="height: {messageCount * 50}px;width: 100%;" />
		{/if}
	</div>
{:else}
	<div>
		{#each splitMessages as message (message['id'])}
			<!-- skip thread start msg -->
			{#if message.type !== '21'}
				<Message {message} {messages} {guild} {guildId} {search}/>
			{/if}
		{/each}
	</div>
{/if}
