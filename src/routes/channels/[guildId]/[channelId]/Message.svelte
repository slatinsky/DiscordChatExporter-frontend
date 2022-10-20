<script>
	import { nameRenderer } from '../../../settingsStore';
	import { onMount, onDestroy } from 'svelte';
	import { fade } from 'svelte/transition';
	import MessageContent from './MessageContent.svelte';
	import { renderTimestamp } from '../../../time';

	export let message;
	// export let messages;
	export let guild;
	export let search = false;

	let DEBUG = false;

	// https://svelte.dev/repl/4b8ccdf1d01545baa0ab6a858bc05abb?version=3.32.1
	let loaded = false;
	let root;

	let observer = new IntersectionObserver(
		(entries) => {
			entries.forEach((entry) => {
				if (entry.isIntersecting) {
					processMessage();

					observer.disconnect();

					loaded = true;
				}
			});
		},
		{
			rootMargin: '100% 0px 100% 0px',
			threshold: 0.1
		}
	);

	onMount(() => {
		observer.observe(root);
	});

	onDestroy(() => {
		observer.disconnect();
	});

	function processMessage() {
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
		} else {
			return full_name(author);
		}
	}

	function addAuthorToMessage() {
		if (message.authorId) {
			message.author = guild.authors[message.authorId];
			// delete message.authorId;
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
					// delete reaction.emojiId;
					message = message; // apply changes
				}

				if (reaction.emojiName) {
					reaction.emoji = guild.emojis[reaction.emojiName];
					// delete reaction.reactionId;
					message = message; // apply changes
				}
			}
		}
	}

	function addReferencedMessage() {
		if (message.reference) {
			// console.log(message.reference);
			message.referencedMessage =
				guild.messages[message.reference.channelId][message.reference.messageId];
			if (message.referencedMessage && message.referencedMessage?.authorId) {
				message.referencedMessage.author = guild.authors[message.referencedMessage.authorId];
				// delete message.referencedMessage.authorId;
			}
			// console.log(message.reference, message.referencedMessage, messages.length, Object.keys(messages)[0]);
		}
	}
</script>

<!-- Rewritten https://github.com/Tyrrrz/DiscordChatExporter/blob/master/DiscordChatExporter.Core/Exporting/Writers/Html/MessageGroupTemplate.cshtml to svelte -->
<div bind:this={root}>
	{#if loaded}
		{#if search&& message.searchPrevMessageChannelId && message.searchPrevMessageChannelId !== message.channelId}
			<div class="channel-name"><a href="/channels/{guild.id}/{message.channelId}/"># {guild.channels[message.channelId]?.name}</a></div>
		{/if}
		<div class="chatlog__message-group" transition:fade={{ duration: 125 }}>
			<!-- <button on:click={()=>copyTextToClipboard(message.id)}>Copy ID</button> -->
			<div
				id="{search ? 'search-id-' : ''}{message.id}"
				class="chatlog__message-container {message.isPinned
					? 'chatlog__message-container--pinned'
					: ''}"
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
							<img
								class="chatlog__avatar"
								src={message.author?.localFilePath}
								alt="Avatar"
								loading="lazy"
							/>
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
											src={message.referencedMessage.author?.localFilePath}
											alt="Avatar"
											loading="lazy"
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
												>{message.referencedMessage.content}</span
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
									></span
								>
							</div>
							<div class="chatlog__content chatlog__markdown">
								<span class="chatlog__markdown-preserve"
									><MessageContent content={message.content} /></span
								>
								{#if message.timestampEdited != null}
									<span class="chatlog__edited-timestamp" title={message.timestampEdited}
										>(edited)</span
									>
								{/if}
							</div>
							{#if message.attachments}
								{#each message.attachments as attachment}
									{#if attachment.type == 'image'}
										<div class="chatlog__attachment">
											<a href={attachment?.localFilePath} target="_blank">
												<img
													class="chatlog__attachment-media"
													src={attachment?.localFilePath}
													alt="Attachment"
													title="Image: {attachment.fileName} ({attachment.fileSizeBytes} B)"
													loading="lazy"
												/>
											</a>
										</div>
									{:else if attachment.type == 'video'}
										<video class="chatlog__attachment-media" controls>
											<source src="{attachment?.localFilePath}" alt="{attachment?.Description ?? 'Video attachment'}" title="Video: {attachment.fileName} ({attachment.fileSizeBytes} B)">
										</video>
									{:else}
										<div class="chatlog__attachment">
											<a href={attachment?.localFilePath} target="_blank">
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
														<a href={attachment?.localFilePath} target="_blank">
															{attachment.fileName}
														</a>
													</div>
													<div class="chatlog__attachment-generic-size">
														{Math.round(attachment.fileSizeBytes / 1024)} KB
													</div>
												</div>
											</a>
										</div>
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
														<!-- embed.author.iconUrl -->
														{#if embed.author.localFilePath}
															<img class="chatlog__embed-author-icon" src="{embed.author.localFilePath}" alt="Author icon" loading="lazy" onerror="this.style.visibility='hidden'">
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
															<a class="chatlog__embed-title-link" href="@embed.Url">
																<div class="chatlog__markdown chatlog__markdown-preserve">{embed.title}</div>
															</a>
														{:else}
															<div class="chatlog__markdown chatlog__markdown-preserve">{embed.title}</div>
														{/if}
													</div>
												{/if}

												<!-- @{/* Embed description */} -->
												{#if embed.description}
													<div class="chatlog__embed-description">
														<div class="chatlog__markdown chatlog__markdown-preserve">{embed.description}</div>
													</div>
												{/if}

												<!-- @{/* Embed fields */} -->
												{#if embed.fields}
													<div class="chatlog__embed-fields">
														{#each embed.fields as field}
															<div class="chatlog__embed-field">
																{#if field.name}
																	<div class="chatlog__embed-field-name">
																		<div class="chatlog__markdown chatlog__markdown-preserve">{field.name}</div>
																	</div>
																{/if}

																{#if field.value}
																	<div class="chatlog__embed-field-value">
																		<div class="chatlog__markdown chatlog__markdown-preserve">{field.value}</div>
																	</div>
																{/if}
															</div>
														{/each}
													</div>
												{/if}


											<!-- @{/* Embed content */} -->
												{#if embed.thumbnail}
													<div class="chatlog__embed-thumbnail-container">
														<a class="chatlog__embed-thumbnail-link" href="{embed.thumbnail?.localFilePath}" target="_blank">
															<img class="chatlog__embed-thumbnail" src="{embed.thumbnail?.localFilePath}" alt="Thumbnail" loading="lazy">
														</a>
													</div>
												{/if}

												<!-- @{/* Embed images */} -->
												{#if embed.images}
													{#each embed.images as image}
														<div class="chatlog__embed-images">
															<div class="chatlog__embed-image-container">
																<a class="chatlog__embed-image-link" href="{image.localFilePath}" target="_blank">
																	<img class="chatlog__embed-image" src="{image.localFilePath}" alt="Image" loading="lazy">
																</a>
															</div>
														</div>
													{/each}
												{/if}

												<!-- @{/* Embed footer & icon */} -->
												{#if embed.footer}
													<div class="chatlog__embed-footer">
														{#if embed.footer.localFilePath}
															<img class="chatlog__embed-footer-icon" src="{embed.footer.localFilePath}" alt="Footer icon" loading="lazy">
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
						<!--                TODO: stickers-->
						<!--                REACTIONS-->
						<div class="chatlog__reactions">
							{#if message.reactions}
								{#each message.reactions as reaction}
									<div class="chatlog__reaction" title={reaction.emoji.name}>
										<img
											class="chatlog__emoji chatlog__emoji--small"
											alt="{reaction.emoji.name}"
											src={reaction.emoji?.localFilePath}
											loading="lazy"
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
		<div class="not-loaded" id={message.id} />
	{/if}
</div>

<style>
	.not-loaded {
		height: 50px;
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

	.chatlog__attachment-media {
		max-width: calc(100% - 10px);
	}
</style>
