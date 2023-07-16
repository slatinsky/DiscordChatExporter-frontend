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

		// if is system notification, don't merge
		if (isSystemNotification(message.type)) {
			return false;
		}

		// if nicknames are different, don't merge
		if (previousMessage.author.nickname !== message.author.nickname) {
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


	function isSystemNotification(messageType: string): boolean {
		// https://github.com/Tyrrrz/DiscordChatExporter/blob/81a6d363d1e503787e1aebc5e30b411ef796ef77/DiscordChatExporter.Core/Discord/Data/MessageKind.cs#L20
		const systemNotificationTypes = [
			"RecipientAdd",  // 1
			"RecipientRemove",  // 2
			"Call",  // 3
			"ChannelNameChange",  // 4
			"ChannelIconChange",  // 5
			"ChannelPinnedMessage",  // 6
			"GuildMemberJoin",  // 7
			"ThreadCreated",  // 18
		]

		const notSystemNotificationTypes = [
			"Default",  // 0
			"Reply",  // 19
		]

		return systemNotificationTypes.includes(messageType)
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

				<!-- system notifications -->
				{#if isSystemNotification(message.type)}
					<div class="chatlog__message-aside">
						<svg class="chatlog__system-notification-icon">
							{#if message.type == "RecipientAdd"}
								<path fill="#3ba55c" d="m0 8h14.2l-3.6-3.6 1.4-1.4 6 6-6 6-1.4-1.4 3.6-3.6h-14.2" />
							{:else if message.type == "RecipientRemove"}
								<path fill="#ed4245" d="m3.8 8 3.6-3.6-1.4-1.4-6 6 6 6 1.4-1.4-3.6-3.6h14.2v-2" />
							{:else if message.type == "Call"}
								<path fill="#3ba55c" fill-rule="evenodd" d="M17.7163041 15.36645368c-.0190957.02699568-1.9039523 2.6680735-2.9957762 2.63320406-3.0676659-.09785935-6.6733809-3.07188394-9.15694343-5.548738C3.08002193 9.9740657.09772497 6.3791404 0 3.3061316v-.024746C0 2.2060575 2.61386252.3152347 2.64082114.2972376c.7110335-.4971705 1.4917101-.3149497 1.80959713.1372281.19320342.2744561 2.19712724 3.2811005 2.42290565 3.6489167.09884826.1608492.14714912.3554431.14714912.5702838 0 .2744561-.07975258.5770327-.23701117.8751101-.1527655.2902036-.65262318 1.1664385-.89862055 1.594995.2673396.3768148.94804468 1.26429792 2.351016 2.66357424 1.39173858 1.39027775 2.28923588 2.07641807 2.67002628 2.34187563.4302146-.2452108 1.3086162-.74238132 1.5972981-.89423205.5447887-.28682915 1.0907006-.31944893 1.4568885-.08661115.3459689.2182151 3.3383754 2.21027167 3.6225641 2.41611376.2695862.19234426.4144887.5399137.4144887.91672846 0 .2969525-.089862.61190215-.2808189.88523346" />
							{:else if message.type == "ChannelNameChange" || message.type == "ChannelIconChange"}
								<path fill="#99aab5" d="m0 14.25v3.75h3.75l11.06-11.06-3.75-3.75zm17.71-10.21c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75z" />
							{:else if message.type == "ChannelPinnedMessage"}
								<path fill="#b9bbbe" d="m16.908 8.39684-8.29587-8.295827-1.18584 1.184157 1.18584 1.18584-4.14834 4.1475v.00167l-1.18583-1.18583-1.185 1.18583 3.55583 3.55502-4.740831 4.74 1.185001 1.185 4.74083-4.74 3.55581 3.555 1.185-1.185-1.185-1.185 4.1475-4.14836h.0009l1.185 1.185z" />
							{:else if message.type == "GuildMemberJoin"}
								<path fill="#3ba55c" d="m0 8h14.2l-3.6-3.6 1.4-1.4 6 6-6 6-1.4-1.4 3.6-3.6h-14.2" />
							{:else if message.type == "ThreadCreated"}
								<path fill="#b9bbbe" d="M5.43309 21C5.35842 21 5.30189 20.9325 5.31494 20.859L5.99991 17H2.14274C2.06819 17 2.01168 16.9327 2.02453 16.8593L2.33253 15.0993C2.34258 15.0419 2.39244 15 2.45074 15H6.34991L7.40991 9H3.55274C3.47819 9 3.42168 8.93274 3.43453 8.85931L3.74253 7.09931C3.75258 7.04189 3.80244 7 3.86074 7H7.75991L8.45234 3.09903C8.46251 3.04174 8.51231 3 8.57049 3H10.3267C10.4014 3 10.4579 3.06746 10.4449 3.14097L9.75991 7H15.7599L16.4523 3.09903C16.4625 3.04174 16.5123 3 16.5705 3H18.3267C18.4014 3 18.4579 3.06746 18.4449 3.14097L17.7599 7H21.6171C21.6916 7 21.7481 7.06725 21.7353 7.14069L21.4273 8.90069C21.4172 8.95811 21.3674 9 21.3091 9H17.4099L17.0495 11.04H15.05L15.4104 9H9.41035L8.35035 15H10.5599V17H7.99991L7.30749 20.901C7.29732 20.9583 7.24752 21 7.18934 21H5.43309Z" />
								<path fill="#b9bbbe" d="M13.4399 12.96C12.9097 12.96 12.4799 13.3898 12.4799 13.92V20.2213C12.4799 20.7515 12.9097 21.1813 13.4399 21.1813H14.3999C14.5325 21.1813 14.6399 21.2887 14.6399 21.4213V23.4597C14.6399 23.6677 14.8865 23.7773 15.0408 23.6378L17.4858 21.4289C17.6622 21.2695 17.8916 21.1813 18.1294 21.1813H22.5599C23.0901 21.1813 23.5199 20.7515 23.5199 20.2213V13.92C23.5199 13.3898 23.0901 12.96 22.5599 12.96H13.4399Z" />
							{/if}
						</svg>
					</div>
					<div class="chatlog__message-primary">
						<span
							class="chatlog__system-notification-author"
							style="color:{message.author.color}"
							title={full_name(message.author)}
							data-user-id={full_name(message.author)}>{nickname(message.author)}
						</span>

						<!-- Space out the content -->
						<span> </span>

						<!-- System notification content -->
						<span class="chatlog__system-notification-content">
							{#if message.type == "RecipientAdd"}
								{#if !message.mentions}
									<!-- fallback, you should not see this one  -->
									<span>added someone to the group</span>
								{:else}
									<span>added <a class="chatlog__system-notification-link" title={message.mentions[0].name}>{message.mentions[0].nickname}</a> to the group</span>
								{/if}
							{:else if message.type == "RecipientRemove"}
								{#if !message.mentions}
									<!-- fallback, you should not see this one  -->
									<span>RecipientRemove</span>
								{:else}
									{#if message.author._id == message.mentions[0]._id}
										<span>left the group</span>
									{:else}
										<span>removed <a class="chatlog__system-notification-link" title={message.mentions[0].name}>{message.mentions[0].nickname}</a> from the group</span>
									{/if}
								{/if}
							{:else if message.type == "Call"}
								<!-- TODO: <span>started a call that lasted @(((message.CallEndedTimestamp ?? message.Timestamp) - message.Timestamp).TotalMinutes) minutes</span> -->
								<span>started a call that lasted {Math.floor((Date.parse(message.callEndedTimestamp ?? message.timestamp) - Date.parse(message.timestamp)) / 60000)} minutes</span>
							{:else if message.type == "ChannelNameChange"}
								<!-- <span>changed the channel name: </span> -->
								<span class="chatlog__system-notification-link">{message.content[0].content[0].toLowerCase()}{message.content[0].content.slice(1)}</span>
							{:else if message.type == "ChannelIconChange"}
								<span>changed the channel icon.</span>
							{:else if message.type == "ChannelPinnedMessage"}
								{#if message?.reference?.messageId}
									<span>pinned a message {message.reference.messageId} to this channel.</span>
								{:else}
									<span>pinned a message to this channel.</span>
								{/if}
							{:else if message.type == "ThreadCreated"}
								<span>started a thread.</span>
							{:else if message.type == "GuildMemberJoin"}
								<span>joined the server.</span>
							{:else}
								<span>{message.content[0].content.toLowerCase()}</span>
							{/if}
						</span>
					</div>
				{:else}
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
				{/if}
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
