<script>
	import { copyTextToClipboard } from '../../../../helpers';
	import MessageGroup from './MessageGroup.svelte';
	export let messages;
	export let authors;
	export let emojis;

	export let guildId;
	export let channelId;

	// }

	// console.error('messages-----',  Object.keys(messages)[0]);


</script>

<div id="top" />

{#key channelId}
	<MessageGroup messages={messages} splitMessages={Object.values(messages)} {authors} {emojis} {guildId}></MessageGroup>
{/key}

<div id="bottom" />

<style>
</style>
