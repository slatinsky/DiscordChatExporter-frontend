<script>
	import { copyTextToClipboard } from '../../../../helpers';
	import { onlyMatches, foundMessageIds, searchTerm} from './searchStore';
	export let messages = {};
	export let authors = {};
	export let emojis = {};

	let page = 0;
	let pageSize = 300;
	$: pages = Math.ceil(messages.length / pageSize);
	$: pageMessages = messages.slice(page * pageSize, (page + 1) * pageSize);


	function prevPage() {
		if (page > 0) {
			page--;
		}
	}



	function nextPage() {
		if (page < pages - 1) {
			page++;
		}
	}


	function human_timestamp_format(timestamp) {
		return timestamp.replace('T', ' ').split('.')[0];
	}

	function full_name(author) {
		return author.name + '#' + author.discriminator;
	}

	function addAuthorsToMessages(pageMessages, authors) {
		// go through each message, messages is object

		for (var messageId of Object.keys(pageMessages)) {
			let message = pageMessages[messageId];

			// add author to message
			if (message.authorId) {
				message.author = authors[message.authorId];
				delete message.authorId;
			}

			// apply changes
			pageMessages[messageId] = message;
		}

		return pageMessages;
	}

	function addEmojisToMessages(pageMessages, emojis) {
		// go through each message, messages is object

		for (var messageId of Object.keys(pageMessages)) {
			let message = pageMessages[messageId];

			if (message.reactions) {
				for (let i = 0; i < message.reactions.length; i++) {
					let reaction = message.reactions[i];

					// add emoji to reaction
					if (reaction.emojiId) {
						reaction.emoji = emojis[reaction.emojiId];
						delete reaction.emojiId;
					}

					if (reaction.emojiName) {
						reaction.emoji = emojis[reaction.emojiName];
						delete reaction.reactionId;
					}

					// apply changes
					message.reactions[i] = reaction;
				}
			}
		}
		return pageMessages;
	}

    function addReferencedMessages(pageMessages) {
        for (var messageId of Object.keys(pageMessages)) {
            let message = pageMessages[messageId];

            if (message.reference) {
                console.log(message.reference);
                message.referencedMessage = pageMessages.find(m => m.id === message.reference.messageId);
                console.log(message.referencedMessage);
            }
        }
        return pageMessages;
    }

    $: console.log("mmmm", pageMessages);

	$: pageMessages = addAuthorsToMessages(pageMessages, authors);
	$: pageMessages = addEmojisToMessages(pageMessages, emojis);
	$: pageMessages = addReferencedMessages(pageMessages);
	// $: console.log('authors', authors);
	// $: console.log('messages', messages);
</script>

<button on:click={prevPage}>PREV PAGE</button>
<button on:click={nextPage}>NEXT PAGE</button>
<div>Page {page+1} of {pages}</div>
{#each Object.values(pageMessages) as message}
	<!-- <p>{message.content} {message.author}</p> -->
	{#if !$onlyMatches || $searchTerm == "" || $foundMessageIds.includes(message.id)}
		<div class="chatlog__message-group">
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

						<img
							class="chatlog__avatar"
							src={message.author.localFilePath}
							alt="Avatar"
							loading="lazy"
						/>
					</div>

					<div class="chatlog__message-primary">
						{#if message.referencedMessage}
                        <a href="#{message.referencedMessage.id}">
							<div class="chatlog__reference">
								<img
									class="chatlog__reference-avatar"
									src={message.referencedMessage.author.localFilePath}
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
								title={message.author.nickname}
								data-user-id={message.author.id}>{message.author.nickname}</span
							>
							<span class="chatlog__timestamp"
								><a href="#{message.id}"
									>{human_timestamp_format(message.timestamp)}</a
								></span
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
										<a href={attachment.localFilePath}>
											<img
												class="chatlog__attachment-media"
												src={attachment.localFilePath}
												alt="Attachment"
												title="Image: {attachment.fileName} ({attachment.fileSizeBytes} KB)"
												loading="lazy"
											/>
										</a>
									</div>
								{:else}
									<div class="chatlog__attachment">
										<a href={attachment.localFilePath} target="_blank">
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
														<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
														<polyline points="14 2 14 8 20 8" />
														<line x1="16" y1="13" x2="8" y2="13" />
														<line x1="16" y1="17" x2="8" y2="17" />
														<polyline points="10 9 9 9 8 9" />
													</svg>
												</svg>
												<div class="chatlog__attachment-generic-name">
													<a href={attachment.localFilePath} target="_blank">
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

						<!-- {#each message.embeds as embed}
                    <div class=chatlog__embed><a
                            href={embed.url}>
                        <img class=chatlog__embed-generic-image
                             src={embed.thumbnail.url}
                             alt="Embedded image" loading=lazy> </a></div>
                {/each} -->
						<!--                TODO: stickers-->
						<!--                REACTIONS-->
						<div class="chatlog__reactions">
							{#if message.reactions}
								{#each message.reactions as reaction}
									<div class="chatlog__reaction" title={reaction.emoji.name}>
										<img
											class="chatlog__emoji chatlog__emoji--small"
											alt="🍰"
											src={reaction.emoji.localFilePath}
											loading="lazy"
										/> <span class="chatlog__reaction-count">{reaction.count}</span>
									</div>
								{/each}
							{/if}
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
	<!-- <pre>{JSON.stringify(message, null, 2)}</pre> -->
{/each}
