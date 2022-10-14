<script>
	import { copyTextToClipboard } from '../../../../helpers';
	import Message from './Message.svelte';
	export let messages;
	export let authors;
	export let emojis;

	export let guildId;

	// }

	// console.error('messages-----',  Object.keys(messages)[0]);


</script>

<div id="top" />

{#each Object.values(messages) as message (message['id'])}
	<Message message={message} messages={messages} {authors} {emojis} {guildId} />
{/each}
<div id="bottom" />

<style>
</style>
