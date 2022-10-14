<script>
	import { onMount, onDestroy } from 'svelte';
    import { fade } from "svelte/transition";


	export let message;
	export let messages;
	export let authors;
	export let emojis;
	export let guildId;

	// https://svelte.dev/repl/4b8ccdf1d01545baa0ab6a858bc05abb?version=3.32.1
	let loaded = false;
	let root;

	let observer = new IntersectionObserver((entries) => {
		entries.forEach((entry) => {
			if (entry.isIntersecting) {
                processMessage()

				observer.disconnect();

                loaded = true;
			}
		});
	}, {
        rootMargin: '100% 0px 100% 0px',
        threshold: .1
    });

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

	function human_timestamp_format(timestamp) {
		return timestamp.replace('T', ' ').split('.')[0];
	}

	function full_name(author) {
		return author.name + '#' + author.discriminator;
	}

    function nickname(author) {
        return author?.nickname ?? full_name(message.author)
    }

	function addAuthorToMessage() {
		if (message.authorId) {
			message.author = authors[message.authorId];
			delete message.authorId;
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
					reaction.emoji = emojis[reaction.emojiId];
					delete reaction.emojiId;
					message = message; // apply changes
				}

				if (reaction.emojiName) {
					reaction.emoji = emojis[reaction.emojiName];
					delete reaction.reactionId;
					message = message; // apply changes
				}
			}
		}
	}

	function addReferencedMessage() {
		if (message.reference) {
			// console.log(message.reference);
			message.referencedMessage = messages[message.reference.messageId];
            if (message.referencedMessage && message.referencedMessage?.authorId) {
                message.referencedMessage.author = authors[message.referencedMessage.authorId];
                delete message.referencedMessage.authorId;
                // message = message; // apply changes
            }
			// console.log(message.reference, message.referencedMessage, messages.length, Object.keys(messages)[0]);
		}
	}

</script>

<div bind:this={root}>
	{#if loaded}
		<div class="chatlog__message-group" transition:fade={{duration: 125}}>
			<!-- <button on:click={()=>copyTextToClipboard(message.id)}>Copy ID</button> -->
			<div
				id={message.id}
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
                        <a href="/channels/{guildId}/{message.reference.channelId}">
							<div class="chatlog__message-primary thread-created">
                                <div><span class="thread-name">{message.threadName}</span> <span class="thread-msg-count">{message.threadMsgCount} messages</span></div>
								<span
									class="chatlog__system-notification-author"
									style="color:{message.author.color}"
									title={full_name(message.author)}
									data-user-id={full_name(message.author)}>{nickname(message.author)}</span
								>

								<span class="chatlog__system-notification-content">
									<span
										>
											started a thread.</span
									>
								</span>
								<span class="chatlog__system-notification-timestamp">
									<a href="#chatlog__message-container-{message.reference.channelId}"
										>{human_timestamp_format(message.timestamp)}</a
									>
								</span>
							</div>
                        </a>

							<!-- <div class="message thread-created">
                        <div class="message-header">
                            <div class="message-header-left">
                                <div class="message-author">
                                    {message.author ? message.author.name : 'Unknown'}
                                </div>
                                <div class="message-timestamp">
                                    {human_timestamp_format(message.timestamp)}
                                </div>
                            </div>
                            <div class="message-header-right">
                                <div class="message-id">
                                    {message.id}
                                </div>
                                <div class="message-copy-id" on:click={() => copyTextToClipboard(message.id)}>
                                    Copy ID
                                </div>
                            </div>
                        </div>
                        <div class="message-content">
                            <div class="message-content-text">
                                {message.content}
                            </div>
                        </div>
                    </div> -->
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
												onclick="scrollToMessage(event,message.reference.messageId)"
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
									><a href="#{message.id}">{human_timestamp_format(message.timestamp)}</a></span
								>
							</div>
							<div class="chatlog__content chatlog__markdown">
								<span class="chatlog__markdown-preserve">{message.content}</span>
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
													title="Image: {attachment.fileName} ({attachment.fileSizeBytes} KB)"
													loading="lazy"
												/>
											</a>
										</div>
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
								{#if embed.thumbnail}
									<div class="chatlog__embed">
										<a href={embed.thumbnail?.localFilePath} target="_blank">
											<img
												class="chatlog__embed-generic-image"
												src={embed.thumbnail?.localFilePath}
												alt="Embedded image"
												loading="lazy"
											/>
										</a>
									</div>
								{/if}
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
											alt="🍰"
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
            <!-- <pre>{JSON.stringify(message, null, 2)}</pre> -->
		</div>
        {:else}
        <div class="not-loaded" id={message.id}></div>
	{/if}
</div>


<style>
    .not-loaded {
        height: 50px;
        width: 100%;
    }

    .thread-created {
        background-color: #2F3136;
        padding: 15px 10px;
    }

    .thread-name {
        font-weight: 600;
        color: #fff;
        margin-bottom: 5px;
    }

    .thread-msg-count {
        font-weight: 600;
        color: #0FAFF4;
        margin-left: 10px;
    }
</style>