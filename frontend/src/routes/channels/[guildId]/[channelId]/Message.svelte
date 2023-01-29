<script>
	import { nameRenderer, linkHandler, unloadMessages } from '../../../settingsStore';
	import { onMount, onDestroy } from 'svelte';
	import { fade } from 'svelte/transition';
	import MessageMarkdown from './MessageMarkdown.svelte';
	import ContextMenu from '../../../../components/menu/ContextMenu.svelte';
	import MenuOption from '../../../../components/menu/MenuOption.svelte';
	import { setMenuVisible, isMenuVisible } from '../../../../components/menu/menuStore';
	import { copyTextToClipboard, checkUrl, getFileNameFromUrl } from '../../../../js/helpers';
	import { renderTimestamp } from '../../../../js/time';
	import ImageGallery from './ImageGallery.svelte';

	export let message;
	export let guild;
	export let search = false;
	export let rootId

	let DEBUG = false;

	// https://svelte.dev/repl/4b8ccdf1d01545baa0ab6a858bc05abb?version=3.32.1
	// processMessage();
	let loaded = false;
	let root;
	let isVisible = false;

	let sheduledToBeHidden = false;

	let placeholderHeight = 75;

	let observer = new IntersectionObserver(
		(entries) => {
			entries.forEach((entry) => {
				if (entry.isIntersecting) {
					processMessage();

					// observer.disconnect();

					loaded = true;
					isVisible = true;
					sheduledToBeHidden = false;
					// console.log("message loaded", message.id);
				}
			});
		},
		{
			root: rootId,
			rootMargin: '200% 0px',
			threshold: 0
		}
	);

	let unloadObserver = new IntersectionObserver(
		(entries) => {
			entries.forEach((entry) => {
				if (!entry.isIntersecting) {
					sheduledToBeHidden = true;
					setTimeout(() => {
						if (sheduledToBeHidden) {
							// get height of element
							placeholderHeight = root.offsetHeight;
							isVisible = false;
							sheduledToBeHidden = false;
							// console.log("message unloaded", message.id);

						}
						else {
							// console.log("message not unloaded", message.id);
						}
					}, 10000);
				}
			});
		},
		{
			root: rootId,
			rootMargin: '1000% 0px',
			threshold: 0
		}
	);

	onMount(() => {
		observer.observe(root);
		if ($unloadMessages) {
			unloadObserver.observe(root);
		}
	});

	onDestroy(() => {
		observer.disconnect();
		if ($unloadMessages) {
			unloadObserver.disconnect();
		}
	});


	function processMessage() {
		console.log();
		addAuthorToMessage();
		addEmojiToMessage();
		addReferencedMessage();
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

	function addAuthorToMessage() {
		if (message.authorId) {
			message.author = guild.authors[message.authorId];
			message = message; // apply changes
		}
	}

	function addEmojiToMessage() {
		// go through each message, messages is object
		if (message.reactions) {
			for (let i = 0; i < message.reactions.length; i++) {
				let reaction = message.reactions[i];

				// add emoji to reaction
				if (reaction.emojiId) {
					reaction.emoji = guild.emojis[reaction.emojiId];
					message = message; // apply changes
				}

				if (reaction.emojiName) {
					reaction.emoji = guild.emojis[reaction.emojiName];
					message = message; // apply changes
				}
			}
		}
	}

	function addReferencedMessage() {
		if (message.reference) {
			try {
				message.referencedMessage = guild.messages[message.reference.channelId][message.reference.messageId];
			} catch (e) {
				console.warn("Couldn't find referenced message");  // if channel is not exported and we try to get first referenced message from thread
			}
			if (message.referencedMessage && message.referencedMessage?.authorId) {
				message.referencedMessage.author = guild.authors[message.referencedMessage.authorId];
			}
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
<div bind:this={root} class="msg-root">
	{#if loaded && isVisible}
		{#if search&& message.searchPrevMessageChannelId && message.searchPrevMessageChannelId !== message.channelId}
			<div class="channel-name"><a href="/channels/{guild.id}/{message.channelId}/"># {guild.channels[message.channelId]?.name}</a></div>
		{/if}
		<div class="chatlog__message-group" transition:fade={{ duration: 125 }} on:contextmenu|preventDefault={e=>onRightClick(e, message)}>
			<div
				id="{search ? 'search-id-' : ''}{message.id}"
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

						{#if message.type != 'ThreadCreated'}
							<ImageGallery url={message.author?.avatarUrl} imgclass={"chatlog__avatar"} />
						{/if}
					</div>

					<div class="chatlog__message-primary">
						{#if message.type == 'ThreadCreated'}
							<a href="/channels/{guild.id}/{message.reference.channelId}">
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
							{#if message.referencedMessage}
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
												><MessageMarkdown content={message.referencedMessage.content.replace("\n", " ")} {guild} {message} /></span
											>
										</div>
									</div>
								</a>
							{/if}
							<div class="chatlog__header">
								<span
									class="chatlog__author"
									title={nickname(message.author)}
									style="color:{message.author.color}"
									data-user-id={message.author.id}>{nickname(message.author)}</span
								>
								<span class="chatlog__timestamp"
									><a href="/channels/{guild.id}/{message.channelId}#{message.id}"
										>{renderTimestamp(message.timestamp)}</a
									>
									</span
								>
							</div>
							<div class="chatlog__content chatlog__markdown">
								<span class="chatlog__markdown-preserve"
									><MessageMarkdown content={message.content} {guild} {message} /></span
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
								{#each message.attachments as attachment}
									{#if attachment.url.type == 'image'}
										<div class="chatlog__attachment">
											<ImageGallery url={attachment?.url} imgclass={"chatlog__attachment-media"} />
										</div>

									{:else if attachment.url.type == 'video'}
									<div class:media-spoiler={getFileNameFromUrl(attachment?.url?.url).startsWith('SPOILER')}>
										<!-- title -->
										<div class="chatlog__attachment">
											<a href={checkUrl(attachment?.url?.url)} target="_blank">
												<div class="chatlog__attachment-media">
													<div class="chatlog__attachment-media-title">
														{attachment.fileName}
													</div>
												</div>
											</a>
										</div>
										<video class="chatlog__attachment-media" controls preload="metadata">
											<source src="{checkUrl(attachment?.url?.url)}" alt="{attachment?.Description ?? 'Video attachment'}" title="Video: {attachment.fileName} ({attachment.fileSizeBytes} B)">
										</video>
									</div>
									{:else}
										<div class="chatlog__attachment">
											<a href={checkUrl(attachment?.url?.url)} target="_blank">
												<div class="chatlog__attachment-generic">
													<svg class="chatlog__attachment-generic-icon">
														<svg
															xmlns="http://www.w3.org/2000/svg"
															width="24"
															height="24"
															viewBox="0 0 24 24"
															fill="none"
															stroke="currentColor"
															stroke-width="2"
															stroke-linecap="round"
															stroke-linejoin="round"
															class="feather feather-file"
														>
															<path
																d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
															/>
															<polyline points="14 2 14 8 20 8" />
															<line x1="16" y1="13" x2="8" y2="13" />
															<line x1="16" y1="17" x2="8" y2="17" />
															<polyline points="10 9 9 9 8 9" />
														</svg>
													</svg>
													<div class="chatlog__attachment-generic-name">
														<a href={checkUrl(attachment?.url?.url)} target="_blank">
															{attachment.fileName}
														</a>
													</div>
													<div class="chatlog__attachment-generic-size">
														{Math.round(attachment.fileSizeBytes / 1024)} KB
													</div>
												</div>
											</a>
										</div>
										{#if attachment.url.type == 'audio'}
										<audio class="chatlog__attachment-media" controls preload="metadata">
											<source src="{checkUrl(attachment?.url?.url)}" alt="{attachment?.Description ?? 'Audio attachment'}" title="Audio: {attachment.fileName} ({attachment.fileSizeBytes} B)">
										</audio>
										{/if}
									{/if}
								{/each}
							{/if}
						{/if}

						{#if message.embeds}
							{#each message.embeds as embed}
								<div class="chatlog__embed">
									<!-- @{/* Color pill */} -->
									{#if embed.color}
										<div class="chatlog__embed-color-pill" style="background-color: {embed.color}"></div>
									{:else}
										<div class="chatlog__embed-color-pill chatlog__embed-color-pill--default"></div>
									{/if}

									<div class="chatlog__embed-content-container">
										<div class="chatlog__embed-content">
											<div class="chatlog__embed-text">
												<!-- @{/* Embed author */} -->
												{#if embed.author}
													<div class="chatlog__embed-author-container">
														<!-- TODO: check url -->
														{#if embed.author?.iconUrl?.url}
															<img class="chatlog__embed-author-icon" src="{checkUrl(embed.author?.iconUrl?.url)}" alt="Author icon" loading="lazy" onerror="this.style.visibility='hidden'"
													width="{embed.author?.width ?? 16}"
													height="{embed.author?.height ?? 16}"
													>
														{/if}
														{#if embed.author.name}
															{#if embed.author.url}
																<a class="chatlog__embed-author-link" href="{embed.author.url}">
																	<div class="chatlog__embed-author">{embed.author.name}</div>
																</a>
															{:else}
																<div class="chatlog__embed-author">{embed.author.name}</div>
															{/if}
														{/if}
													</div>
												{/if}

												<!-- @{/* Embed title */} -->
												{#if embed.title}
													<div class="chatlog__embed-title">
														{#if embed.url}
															<a class="chatlog__embed-title-link" href={embed?.url}>
																<div class="chatlog__markdown chatlog__markdown-preserve"><MessageMarkdown content={embed.title} {guild} {message} /></div>
															</a>
														{:else}
															<div class="chatlog__markdown chatlog__markdown-preserve"><MessageMarkdown content={embed.title} {guild} {message} /></div>
														{/if}
													</div>
												{/if}

												<!-- @{/* Embed description */} -->
												{#if embed.description}
													<div class="chatlog__embed-description">
														<div class="chatlog__markdown chatlog__markdown-preserve"><MessageMarkdown content={embed.description} {guild} {message} /></div>
													</div>
												{/if}

												<!-- @{/* Embed fields */} -->
												{#if embed.fields}
													<div class="chatlog__embed-fields">
														{#each embed.fields as field}
															<div class="chatlog__embed-field">
																{#if field.name}
																	<div class="chatlog__embed-field-name">
																		<div class="chatlog__markdown chatlog__markdown-preserve"><MessageMarkdown content={field.name} {guild} {message} embed={true}/></div>
																	</div>
																{/if}

																{#if field.value}
																	<div class="chatlog__embed-field-value">
																		<div class="chatlog__markdown chatlog__markdown-preserve"><MessageMarkdown content={field.value} {guild} {message} embed={true}/></div>
																	</div>
																{/if}
															</div>
														{/each}
													</div>
												{/if}


											<!-- @{/* Embed content */} -->
												{#if embed.thumbnail}
													<div class="chatlog__embed-thumbnail-container">
															<!-- {console.warn(embed.thumbnail.type)} -->
															{#if embed.thumbnail?.url?.type === 'video'}
																<a class="chatlog__embed-thumbnail-link" href="{embed.thumbnail?.url?.url}" target="_blank">
																	<video class="chatlog__embed-thumbnail-video" src="{checkUrl(embed.thumbnail?.url?.url)}" autoplay loop muted playsinline
																	width="{embed.thumbnail?.width ?? 16}"
																	height="{embed.thumbnail?.height ?? 16}"/>
																</a>
															{:else if embed.thumbnail?.url?.url}
																<ImageGallery url={embed.thumbnail?.url} imgclass={"chatlog__embed-thumbnail"} />
															{/if}
													</div>
												{/if}

												<!-- @{/* Embed images */} -->
												{#if embed.images}
													{#each embed.images as image}
														<div class="chatlog__embed-images">
															<div class="chatlog__embed-image-container">
																<ImageGallery url={image.url} imgclass={"chatlog__embed-image"} />
															</div>
														</div>
													{/each}
												{/if}

												<!-- @{/* Embed footer & icon */} -->
												{#if embed.footer}
													<div class="chatlog__embed-footer">
														{#if embed.footer.url}
															<img class="chatlog__embed-footer-icon" src="{checkUrl(embed.footer.url?.url)}" alt="Footer icon" loading="lazy" onerror="this.style.visibility='hidden'">
														{/if}

														<span class="chatlog__embed-footer-text">
														{#if embed.footer.text}
															{embed.footer.text}
															{#if embed.timestamp}
																{" • "} {embed.timestamp}
															{/if}
														{/if}
														</span>
													</div>
												{/if}
											</div>
										</div>
									</div>
								</div>
							{/each}
						{/if}
						<!-- stickers -->
						{#if message.stickers}
							{#each message.stickers as sticker}
								<div class="chatlog__sticker">
									<ImageGallery url={sticker.url} imgclass={"chatlog__sticker-image"} />
								</div>
							{/each}
						{/if}

						<!--                REACTIONS-->
						<div class="chatlog__reactions">
							{#if message.reactions}
								{#each message.reactions as reaction}
									<div class="chatlog__reaction" title={reaction.emoji.name}>
										<img
											class="chatlog__emoji chatlog__emoji--small"
											alt="{reaction.emoji.name}"
											src={checkUrl(reaction.emoji?.imageUrl.url)}
											loading="lazy"
											width="{reaction.emoji?.imageUrl?.width ?? 17}"
											height="{reaction.emoji?.imageUrl?.height ?? 17}"
											onerror="this.style.visibility='hidden'"
										/> <span class="chatlog__reaction-count">{reaction.count}</span>
									</div>
								{/each}
							{/if}
						</div>
					</div>
				</div>
			</div>
			{#if DEBUG}
				<pre>{JSON.stringify(message, null, 2)}</pre>
			{/if}
		</div>
	{:else}
		<div class="not-loaded" id={message.id} style="height: {placeholderHeight}px;"/>
	{/if}
</div>

{#if rightClickMessage}
	<ContextMenu let:visible>
		<MenuOption
				on:click={() => copyTextToClipboard(BigInt(message.author.id))}
				text="Copy author ID" {visible} />
		<MenuOption
				on:click={() => copyTextToClipboard(BigInt(message.id))}
				text="Copy message ID" {visible} />
		<MenuOption
				on:click={() => copyTextToClipboard(`https://discord.com/channels/${BigInt(guild.id)}/${BigInt(message.channelId)}/${BigInt(message.id)}`)}
				text="Copy message link" {visible} />
		<MenuOption
				on:click={() => window.open(($linkHandler === "app" ? "discord://" : "") + `https://discord.com/channels/${BigInt(guild.id)}/${BigInt(message.channelId)}/${BigInt(message.id)}`,'_blank')}
				text="Open in discord" {visible} />
		<MenuOption
			on:click={() => console.log(JSON.stringify(message, null, 2))}
			text="Print message object to console" {visible} />
	</ContextMenu>
{/if}

<style>
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

	:global([data-hidespoilers="true"] .d-spoiler) {
		background-color: rgba(0, 0, 0, 0.3);
		color: transparent !important;
		border-radius: 3px;
		-webkit-backdrop-filter: blur(10px);
		backdrop-filter: blur(10px);
		cursor: pointer;
	}
	:global([data-hidespoilers="true"] .d-spoiler > *) {
		pointer-events:none;
	}
	:global([data-hidespoilers="true"] .d-spoiler img) {
		visibility: hidden;
	}
	:global([data-hidespoilers="true"] .d-spoiler a) {
		color: transparent !important;
	}

	:global(.d-spoiler-revealed),
	:global([data-hidespoilers="false"] .d-spoiler) {
		background-color: rgba(0, 0, 0, 0.3);
	}

	:global([data-hidespoilers="true"] .media-spoiler) {
		filter: blur(15px);
		cursor: pointer;
	}
	:global([data-hidespoilers="true"] .media-spoiler > *) {
		pointer-events:none;
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
