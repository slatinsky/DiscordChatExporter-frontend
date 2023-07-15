<script lang="ts">
	import { checkUrl, copyTextToClipboard, snowflakeToDate } from 'src/js/helpers';
	import type { Author, Message } from 'src/js/interfaces';
	import { renderDate, renderTimestamp } from 'src/js/time';
	import ImageGallery from 'src/routes/channels/[guildId]/[channelId]/ImageGallery.svelte';
	import { contextMenuItems} from '../menu/menuStore';
	import { linkHandler, nameRenderer } from 'src/routes/settingsStore';
	import MessageAttachments from './MessageAttachments.svelte';
	import MessageEmbeds from './MessageEmbeds.svelte';
	import MessageMarkdown from './MessageMarkdown.svelte';
	import MessageReactions from './MessageReactions.svelte';
	import MessageStickers from './MessageStickers.svelte';
	import { guildId } from 'src/js/stores';

	import identicons from 'identicons'

	export let message: Message;
	export let previousMessage: Message | null = null;
	export let referencedMessage: Message | null = null;
	export let selectedGuildId: string

	let previousMessageFromDifferentChannel = true;
	if (previousMessage && previousMessage.channelId === message.channelId) {
		previousMessageFromDifferentChannel = false;
	}

	$: mergeWithPrevious = shouldMerge(previousMessage, message);


	// should we should visually group this message with the previous one?
	function shouldMerge(previousMessage: Message | null, message: Message) {
		// null checks
		if (!previousMessage) {
			return false;
		}
		if (!message) {
			return false;
		}

		// if from different author, don't merge
		if (previousMessage.author?._id !== message.author._id) {
			return false;
		}

		// if from different channel, don't merge
		if (previousMessage.channelId !== message.channelId) {
			return false;
		}


		// if more than 5 minutes between messages, don't merge
		let prevDate = snowflakeToDate(previousMessage._id);
		let date = snowflakeToDate(message._id);
		if (date.getTime() - prevDate.getTime() > 5 * 60 * 1000) {
			return false;
		}

		// if is reply, don't merge
		if (message.type === "Reply") {
			return false;
		}

		return true;
	}

	$: showDateSeparator = isDateDifferent(previousMessage, message);

	function isDateDifferent(previousMessage: Message | null, message: Message) {
		// null checks
		if (!previousMessage) {
			return true;
		}
		if (!message) {
			return true;
		}

		let prevDate = snowflakeToDate(previousMessage._id);
		let date = snowflakeToDate(message._id);

		return prevDate.getDate() !== date.getDate() || prevDate.getMonth() !== date.getMonth() || prevDate.getFullYear() !== date.getFullYear()
	}


	function full_name(author) {
		return author.name
	}

	function nickname_only(author) {
		return author?.nickname ?? full_name(author);
	}

	function nickname(author: Author): string {
		if ($nameRenderer === 'handle') {
			return full_name(author);
		}
		else if ($nameRenderer === 'nickname') {
			return nickname_only(author);
		}
		else if ($nameRenderer === 'both') {
			return author?.nickname + ' (' + full_name(author) + ')';
		}
		else {
			console.error('Unknown name renderer: ' + $nameRenderer);
		}
	}



	function onRightClick(e, message) {
		$contextMenuItems = [
			{
				"name": "Open in discord",
				"action": () => {
					window.open(($linkHandler === "app" ? "discord://" : "") + `https://discord.com/channels/${BigInt(selectedGuildId)}/${BigInt(message.channelId)}/${BigInt(message._id)}`,'_blank')
				}
			},
			{
				"name": "Copy message link",
				"action": () => {
					copyTextToClipboard(`https://discord.com/channels/${BigInt(selectedGuildId)}/${BigInt(message.channelId)}/${BigInt(message._id)}`);
				}
			},
			{
				"name": "Print message object to console",
				"action": () => {
					console.log(JSON.stringify(message, null, 2))
				}
			},
			{
				"name": "Copy message ID",
				"action": () => {
					copyTextToClipboard(BigInt(message._id))
				}
			},
			{
				"name": "Copy author ID",
				"action": () => {
					copyTextToClipboard(BigInt(message.author._id))
				}
			},
			{
				"name": "Copy author nickname",
				"action": () => {
					copyTextToClipboard(nickname_only(message.author))
				}
			},
			{
				"name": "Copy author name+handle",
				"action": () => {
					copyTextToClipboard(full_name(message.author))
				}
			},
		]
	}
</script>

<!-- Rewritten https://github.com/Tyrrrz/DiscordChatExporter/blob/master/DiscordChatExporter.Core/Exporting/Writers/Html/MessageGroupTemplate.cshtml to svelte -->
<div class="msg-root">

	{#if showDateSeparator}
		<div class="date-separator">
			<div class="date-separator-line"></div>
			<div class="date-separator-text">{renderDate(snowflakeToDate(message._id))}</div>
			<div class="date-separator-line"></div>
		</div>
	{/if}

	<a class="msg-jump" href="/channels/{message.guildId}/{message.channelId}#{message._id}">Jump</a>

	<!-- {#if search && message.searchPrevMessageChannelId && message.searchPrevMessageChannelId !== message.channelId}
		<div class="channel-name"><a href="/channels/{selectedGuildId}/{message.channelId}/"># {guild.channels[message.channelId]?.name}</a></div>
	{/if} -->
	<!-- transition:fade={{ duration: 125 }} -->
	{#if !mergeWithPrevious}
		<div class="padder"></div>
	{/if}

	{#if previousMessageFromDifferentChannel}
		<div class="channel-name"><a href="/channels/{selectedGuildId}/{message.channelId}/"># {message?.channelName}</a></div>
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
			data-message-id={message._id}
		>
			<div class="chatlog__message">
				<!--            TODO: system notification-->
				<!--            Regular message-->
				<div class="chatlog__message-aside">
					{#if message.reference}
						<div class="chatlog__reference-symbol" />
					{/if}

					{#if !mergeWithPrevious}
						{#if message.type != 'ThreadCreated'}
							{#if message.author?.avatar}
								<ImageGallery asset={message.author?.avatar} imgclass={"chatlog__avatar"} />
							{:else}
								<img class="chatlog__avatar" src={identicons.generateSVGDataURIString(message.author._id, { width: 200, size: 3 })} />
							{/if}
						{/if}
					{/if}
				</div>

				<div class="chatlog__message-primary">
					{#if message.type == 'ThreadCreated'}
						<a href="/channels/{selectedGuildId}/{message.reference.channelId}">
							<div class="chatlog__message-primary thread-created">
								<div>
									<span class="thread-name">{message?.thread?.name ?? "Thread not found"}</span>
									{#if message?.thread?.msgCount}
										<span class="thread-msg-count">{message?.thread?.msgCount} messages</span>
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
						{#if referencedMessage}
							<a href="/channels/{message.guildId}/{message.channelId}#{referencedMessage._id}">
								<div class="chatlog__reference">
									<img
										class="chatlog__reference-avatar"
										src={checkUrl(referencedMessage.author?.avatar)}
										alt="Avatar"
										loading="lazy"
										width="{referencedMessage.author?.avatar?.width ?? 16}"
										height="{referencedMessage.author?.avatar?.height ?? 16}"
										onerror="this.style.visibility='hidden'"
									/>
									<div
										class="chatlog__reference-author"
										style="color: {referencedMessage.author.color}"
										title={referencedMessage.author.name}
									>
										{referencedMessage.author.name}
									</div>
									<div class="chatlog__reference-content">
										<span
											class="chatlog__reference-link"
											>
											<MessageMarkdown content={referencedMessage.content[0].content.replace("\n", " ")}/>
											</span
										>
									</div>
								</div>
							</a>
						{:else if message.reference}
							<div class="chatlog__reference">
								<div class="chatlog__reference-content">
									<span
										class="chatlog__reference-link"
										>
										<i>Original message was deleted</i>
										</span
									>
								</div>
							</div>
						{/if}
						{#if !mergeWithPrevious}
							<div class="chatlog__header">
								<span
									class="chatlog__author"
									title={nickname(message.author)}
									style="color:{message.author.color}"
									data-user-id={message.author.id}>{nickname(message.author)}</span
								>
								{#if message.author?.isBot}
									<span class="chatlog__author-tag">BOT</span>
								{/if}
								<span class="chatlog__timestamp"
									><a href="/channels/{selectedGuildId}/{message.channelId}#{message._id}"
										>{renderTimestamp(message.timestamp)}</a
									>
									</span
								>
							</div>
						{/if}
						<div class="chatlog__content chatlog__markdown">
							<span class="chatlog__markdown-preserve"
								>
								<MessageMarkdown content={message.content[0].content} emotes={message?.emotes || undefined} mentions={message?.mentions || undefined} guildId={message?.guildId}/>
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
						<MessageStickers stickers={message.stickers} />
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

	.msg-root .msg-jump {
		visibility: hidden;
		position: absolute;
		top: 3px;
		right: 10px;
		background-color: #1E1E1F;
		color: white;
		font-size: x-small;
		padding: .2rem .3rem;
		border-radius: 2px;
		z-index: 99;
	}

	.msg-root:hover .msg-jump {
		visibility: visible;
	}


	.date-separator {
		display: flex;
		justify-content: center;
		align-items: center;
		margin: 10px 15px;
		gap: 5px;
	}

	.date-separator-line {
		width: 100%;
		height: 1px;
		background-color: #3F4147;
	}

	.date-separator-text {
		color: #949BA4;
		font-size: 12px;
		font-weight: 600;
		white-space: nowrap;  /* never break the line */
	}

	.chatlog__avatar {
		image-rendering: crisp-edges;
		background-color: white;  /*For identicons*/
	}
</style>
