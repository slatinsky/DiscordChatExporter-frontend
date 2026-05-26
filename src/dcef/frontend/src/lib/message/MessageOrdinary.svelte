<script lang="ts">
	import type { Message } from "../../js/interfaces";
	import { getViewUserState } from "../viewuser/viewUserState.svelte";
	import { getRenderablePollEmbed } from "./messagePollData";
	import MessageAttachments from "./MessageAttachments.svelte";
	import MessageAuthorName from "./MessageAuthorName.svelte";
	import MessageAvatar from "./MessageAvatar.svelte";
	import MessageContent from "./MessageContent.svelte";
	import MessageEmbed from "./MessageEmbed.svelte";
	import MessageInvite from "./MessageInvite.svelte";
	import MessagePoll from "./MessagePoll.svelte";
	import MessageReactions from "./MessageReactions.svelte";
	import MessageReferenced from "./MessageReferenced.svelte";
	import MessageStickers from "./MessageStickers.svelte";
	import MessageTimestamp from "./MessageTimestamp.svelte";
	import { onMessageRightClick } from "./messageRightClick";

	export let message: Message;
	export let messageState;
	const viewUserState = getViewUserState();

	function isPollMessage(message: Message): boolean {
		return getRenderablePollEmbed(message) !== null;
	}

	let pollMessage = false;
	$: pollMessage = isPollMessage(message);

	let referencedMessage: Message | null = null;
	$: referencedMessage = message.reference?.message ?? message.referencedMessage ?? null;
</script>

{#if !pollMessage}
	<MessageReferenced {message} {referencedMessage} {messageState} />
{/if}
<div class="avatar-row">
	{#if !messageState.shouldMerge}
		<MessageAvatar author={message.author} on:click={() => viewUserState.setUser(message.author)} {messageState} />
	{:else}
		<div></div>
	{/if}
	<div on:click style="width: 100%;">
		{#if !messageState.shouldMerge}
			<div class="authorline">
				<MessageAuthorName author={message.author} on:click={() => viewUserState.setUser(message.author)} {messageState} />
				<MessageTimestamp channelOrThreadId={message.channelId} timestamp={message.timestamp} messageId={message._id} />
			</div>
		{/if}
		<div class="message-accessories" on:contextmenu|preventDefault={(e) => onMessageRightClick(e, message)}>
			{#if (!messageState.messageContentIsLink || !message.content[0].content.includes("https://tenor.com/view/")) && (!pollMessage || message.content[0].content !== "")}
				<div><MessageContent {message} /></div>
			{/if}
			{#each messageState.inviteIds as inviteId}
				<MessageInvite {inviteId} />
			{/each}
			{#if pollMessage}
				<div><MessagePoll {message} /></div>
			{:else if message.embeds}
				{#each message.embeds as embed}
					<div><MessageEmbed {embed} {messageState} /></div>
				{/each}
			{/if}
			{#if message.attachments}
				<div><MessageAttachments attachments={message.attachments} /></div>
			{/if}
			{#if message.stickers}
				<MessageStickers stickers={message.stickers} />
			{/if}
			<!-- {/if} -->
		</div>
		{#if message.reactions}
			<MessageReactions reactions={message.reactions} />
		{/if}
	</div>
</div>

<style>
	.authorline {
		margin-bottom: 2px;
	}
	.avatar-row {
		display: grid;
		gap: 15px;
		grid-template-columns: 40px 1fr;
		width: 100%;
	}

	.message-accessories {
		width: 100%;
		display: flex;
		flex-direction: column;
		gap: 4px;
	}
</style>
