<script lang="ts">
	import { checkUrl, copyTextToClipboard } from 'src/js/helpers';
	import type { Message } from 'src/js/interfaces';
	import { renderTimestamp } from 'src/js/time';
	import ImageGallery from 'src/routes/channels/[guildId]/[channelId]/ImageGallery.svelte';
	import MenuOption from '../menu/MenuOption.svelte';
	import ContextMenu from '../menu/ContextMenu.svelte';
	import { isMenuVisible, setMenuVisible } from '../menu/menuStore';
	import { linkHandler, nameRenderer } from 'src/routes/settingsStore';
	import MessageAttachments from './MessageAttachments.svelte';
	import MessageEmbeds from './MessageEmbeds.svelte';
	import MessageMarkdown from './MessageMarkdown.svelte';
	import MessageReactions from './MessageReactions.svelte';

	export let message: Message;
	export let previousMessage: Message | null = null;
	export let selectedGuildId: string

	let isSameAuthor = false;

	if (previousMessage && previousMessage.author?._id === message.author._id) {
		isSameAuthor = true;
	}

	function full_name(author) {
		return author.name + '#' + author.discriminator;
	}

	function nickname(author) {
		if ($nameRenderer === 'nickname') {
			return author?.nickname ?? full_name(author);
		}
		else if ($nameRenderer === 'both') {
			return author?.nickname + ' (' + full_name(author) + ')';
		}
		else {
			return full_name(author);
		}
	}

	let rightClickMessage = null;
	function onRightClick(e, message) {
		$isMenuVisible = false  // close previous menu
		setTimeout(() => {
			rightClickMessage = message;
			setMenuVisible(e)
		}, 0);
	}
	$: if (!$isMenuVisible) {
		rightClickMessage = null
	}
</script>

<!-- Rewritten https://github.com/Tyrrrz/DiscordChatExporter/blob/master/DiscordChatExporter.Core/Exporting/Writers/Html/MessageGroupTemplate.cshtml to svelte -->
<div class="msg-root">

	<!-- {#if search && message.searchPrevMessageChannelId && message.searchPrevMessageChannelId !== message.channelId}
		<div class="channel-name"><a href="/channels/{selectedGuildId}/{message.channelId}/"># {guild.channels[message.channelId]?.name}</a></div>
	{/if} -->
	<!-- transition:fade={{ duration: 125 }} -->
	{#if !isSameAuthor}
		<div class="padder"></div>
	{/if}
	<div on:contextmenu|preventDefault={e=>onRightClick(e, message)}>
		<div
			id="{message.id}"
			class="chatlog__message-container {message.isPinned
				? 'chatlog__message-container--pinned'
				: ''}
				{message.isDeleted
					? 'chatlog__message-container--deleted'
					: ''}
				"
			data-message-id={message.id}
		>
			<div class="chatlog__message">
				<!--            TODO: system notification-->
				<!--            Regular message-->
				<div class="chatlog__message-aside">
					{#if message.referencedMessage}
						<div class="chatlog__reference-symbol" />
					{/if}

					{#if !isSameAuthor}
						{#if message.type != 'ThreadCreated'}
							<ImageGallery asset={message.author?.avatar} imgclass={"chatlog__avatar"} />
						{/if}
					{/if}
				</div>

				<div class="chatlog__message-primary">
					{#if message.type == 'ThreadCreated'}
						<a href="/channels/{selectedGuildId}/{message.reference.channelId}">
							<div class="chatlog__message-primary thread-created">
								<div>
									<span class="thread-name">{message.threadName}</span>
									{#if message.threadMsgCount}
										<span class="thread-msg-count">{message.threadMsgCount} messages</span>
									{/if}
								</div>
								<span
									class="chatlog__system-notification-author"
									style="color:{message.author.color}"
									title={full_name(message.author)}
									data-user-id={full_name(message.author)}>{nickname(message.author)}</span
								>

								<span class="chatlog__system-notification-content">
									<span> started a thread.</span>
								</span>
								<span class="chatlog__system-notification-timestamp">
									<a href="#{message.reference.channelId}"
										>{renderTimestamp(message.timestamp)}</a
									>
								</span>
							</div>
						</a>
					{:else}
						{#if message?.referencedMessage}
							<a href="#{message.referencedMessage.id}">
								<div class="chatlog__reference">
									<img
										class="chatlog__reference-avatar"
										src={checkUrl(message.referencedMessage.author?.avatarUrl?.url)}
										alt="Avatar"
										loading="lazy"
										width="{message.referencedMessage.author?.width ?? 16}"
										height="{message.referencedMessage.author?.height ?? 16}"
										onerror="this.style.visibility='hidden'"
									/>
									<div
										class="chatlog__reference-author"
										style="color: {message.referencedMessage.author.color}"
										title={full_name(message.referencedMessage.author)}
									>
										{message.referencedMessage.author.name}
									</div>
									<div class="chatlog__reference-content">
										<span
											class="chatlog__reference-link"
											>
											<!-- <MessageMarkdown content={message.referencedMessage.content.replace("\n", " ")} {guild} {message} /> -->
											</span
										>
									</div>
								</div>
							</a>
						{/if}
						{#if !isSameAuthor}
							<div class="chatlog__header">
								<span
									class="chatlog__author"
									title={nickname(message.author)}
									style="color:{message.author.color}"
									data-user-id={message.author.id}>{nickname(message.author)}</span
								>
								<span class="chatlog__timestamp"
									><a href="/channels/{selectedGuildId}/{message.channelId}#{message.id}"
										>{renderTimestamp(message.timestamp)}</a
									>
									</span
								>
							</div>
						{/if}
						<div class="chatlog__content chatlog__markdown">
							<span class="chatlog__markdown-preserve"
								>
								<MessageMarkdown content={message.content[0].content} />
								</span
							>
							{#if message.timestampEdited != null}
								<span class="chatlog__edited-timestamp" title={message.timestampEdited}
									>(edited)</span
								>
							{/if}
							{#if message.isDeleted}
								<span class="chatlog__edited-timestamp">(deleted)</span>
							{/if}
						</div>
						{#if message.attachments}
							<MessageAttachments attachments={message.attachments} />
						{/if}
					{/if}

					{#if message.embeds}
						<MessageEmbeds embeds={message.embeds} />
					{/if}
					<!-- stickers -->
					{#if message.stickers}
						{#each message.stickers as sticker}
							<div class="chatlog__sticker">
								<ImageGallery asset={sticker.url} imgclass={"chatlog__sticker-image"} />
							</div>
						{/each}
					{/if}

					<!--                REACTIONS-->
					{#if message.reactions}
						<MessageReactions reactions={message.reactions} />
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>

{#if rightClickMessage}
	<ContextMenu let:visible>
		<MenuOption
				on:click={() => copyTextToClipboard(BigInt(message.author._id))}
				text="Copy author ID" {visible} />
		<MenuOption
				on:click={() => copyTextToClipboard(BigInt(message._id))}
				text="Copy message ID" {visible} />
		<MenuOption
				on:click={() => copyTextToClipboard(`https://discord.com/channels/${BigInt(selectedGuildId)}/${BigInt(message.channelId)}/${BigInt(message._id)}`)}
				text="Copy message link" {visible} />
		<MenuOption
				on:click={() => window.open(($linkHandler === "app" ? "discord://" : "") + `https://discord.com/channels/${BigInt(selectedGuildId)}/${BigInt(message.channelId)}/${BigInt(message._id)}`,'_blank')}
				text="Open in discord" {visible} />
		<MenuOption
			on:click={() => console.log(JSON.stringify(message, null, 2))}
			text="Print message object to console" {visible} />
	</ContextMenu>
{/if}

<style>

	.padder {
		height: 15px;
		width: 100%;
	}
	.not-loaded {
		width: 100%;
	}

	.thread-created {
		background-color: #2f3136;
		padding: 15px 10px;
	}

	.thread-name {
		font-weight: 600;
		color: #fff;
		margin-bottom: 5px;
	}

	.thread-msg-count {
		font-weight: 600;
		color: #0faff4;
		margin-left: 10px;
	}

	.channel-name {
		font-weight: 600;
		color: #fff;
		margin-bottom: 5px;
		margin: 15px 30px 5px 15px;
	}

	:global(.chatlog__attachment-media) {
		max-width: calc(100% - 10px);
		object-position:left
	}

	:global(.chatlog__embed-thumbnail) {
		flex: 0;
		max-width: calc(100% - 40px);
		max-height: 100%;
		max-height: auto;
		height: auto;
		margin-top: 1rem;
		margin-left: 1.2rem;
		border-radius: 3px
	}

	.chatlog__embed-thumbnail-video {
		max-width: 100%;
	}

	.chatlog__message-container--deleted {
		background-color: rgba(133, 0, 0, 0.10)
	}

	audio {
		max-width: 80%;
		width: 700px;
	}

	:global(.chatlog__sticker-image) {
		max-width: 200px;
		max-height: auto;
	}
</style>
