<script>
	import { searched, found_messages } from './searchStores';
	import { checkUrl } from '../../../js/helpers';

	export let guild;
	let authors;
	$: authors = guild.authors;
	let all_messages;
	$: all_messages = guild.messages;

	let value = '';
	let filters = [];
	let parsedCursorHere = null;
	let input;

	let isInputFocused = false;
	let cursorPosition = 0;

	function selectFullOption(newKey, newValue) {
		if ('content' in parsedCursorHere) {
			parsedCursorHere.key = newKey;
			parsedCursorHere.value = newValue + ' ';
			reconstructValue();
			clearTimeout(unfocusTimeout);
			setTimeout(() => {
				input.setSelectionRange(value.length, value.length);
				input.focus();
			}, 0);
		}
	}

	function selectOptionKey(newKey) {
		if ('content' in parsedCursorHere) {
			parsedCursorHere.key = newKey;
			parsedCursorHere.value = '';
			delete parsedCursorHere.content;
			reconstructValue();
			clearTimeout(unfocusTimeout);
			setTimeout(() => {
				input.setSelectionRange(value.length, value.length);
				input.focus();
			}, 0);
		}
	}

	function selectOptionValue(newValue) {
		if ('value' in parsedCursorHere) {
			parsedCursorHere.value = newValue + ' ';
			cursorPosition++;
			reconstructValue();
			clearTimeout(unfocusTimeout);
			setTimeout(() => {
				input.setSelectionRange(value.length, value.length);
				input.focus();
			}, 0);
		}
	}

	function reconstructValue() {
		// reconstruct value
		let reconstructedValue = filters
			.map((word) => {
				if (word.key) {
					return word.key + ':' + word.value;
				} else {
					return word.content;
				}
			})
			.join(' ');

		console.log('reconstructedValue', reconstructedValue);
		value = reconstructedValue;
	}

	function inputValueChanged(value) {
		cursorPosition = 0;
		if (input) {
			// update cursor position
			cursorPosition = input.selectionStart;
		}

		// split by space
		let beforeCursor = value.substring(0, cursorPosition);
		let afterCursor = value.substring(cursorPosition, value.length);
		let tempvalue = beforeCursor + '[[[CURSOR_HERE]]]' + afterCursor;
		let words = tempvalue.split(' ');

		// split words by colon
		filters = words.map((word) => {
			let cursorHere = false;
			if (word.includes('[[[CURSOR_HERE]]]')) {
				cursorHere = true;
				word = word.replace('[[[CURSOR_HERE]]]', '');
			}
			let split = word.split(':');

			// if no colon, return word
			if (split.length === 1) {
				let retObj = {
					content: split[0],
					cursorHere: cursorHere
				};
				if (cursorHere) {
					parsedCursorHere = retObj; // set reference
				}
				return retObj;
			} else {
				let retObj = {
					key: split[0],
					value: split[1],
					cursorHere: cursorHere
				};
				if (cursorHere) {
					parsedCursorHere = retObj; // set reference
				}
				return retObj;
			}
		});

		parsedCursorHere = filters.find((word) => word.cursorHere);

		console.log('parsedValue', JSON.stringify(filters, null, 2));
	}

	$: inputValueChanged(value);
	$: console.log('filters', filters);
	$: console.log('parsedCursorHere', parsedCursorHere);

	function removeAccents(str) {
		return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
	}

	function normalizeSearchTerm(str) {
		return removeAccents(str.toLowerCase());
	}

	let unfocusTimeout = null;

	function filterAuthors(authors, _) {
		return Object.values(authors).filter(
			(author) =>
				author.name.toLowerCase().includes(parsedCursorHere.value.toLowerCase()) ||
				author.nickname.toLowerCase().includes(parsedCursorHere.value.toLowerCase())
		);
	}

	function filterChannels(channels, _) {
		return Object.values(channels).filter((channel) =>
			channel.name.toLowerCase().includes(parsedCursorHere.value.toLowerCase())
		).sort((a, b) => {
			// sort by messageCount
			return b.messageCount - a.messageCount;
		});
	}

	function filterEmojis(emojis, _) {
		return Object.values(emojis).filter((emoji) =>
			emoji.name.toLowerCase().includes(parsedCursorHere.value.toLowerCase())
		)
	}

	function filterFiletypes(extensions, _) {
		return Object.values(extensions).filter((extension) =>
			extension.toLowerCase().includes(parsedCursorHere.value.toLowerCase())
		);
	}

	function filterKeys(needle, parsedCursorHere) {
		if (value.includes(needle))
			return false;
		if (parsedCursorHere.content === "") {
			return true
		}
		else if (!parsedCursorHere.content) {
			return false
		}
		else {
			return needle.toLowerCase().includes(parsedCursorHere.content.toLowerCase())
		}
	}

	function findMessages() {
		console.log('searching for messages');
		let found_messages_temp = [];
		let limit = 100;

		console.log('--', Object.keys(all_messages).length, 'messages to search through');
		console.log('--filters', JSON.stringify(filters, null, 2));

		for (const [channelId, channel] of Object.entries(all_messages)) {
			let channelMessages = Object.values(channel);

			for (const filter of filters) {

				if (filter.content) {
					channelMessages = channelMessages.filter((message) => {
						return normalizeSearchTerm(message.content).includes(
							normalizeSearchTerm(filter.content)
						);
					});
				} else if (filter.key !== '' && filter.value === '') {
					// incomplete filter, ignoring
				} else if (filter.key === 'from') {
					let author = Object.values(authors).find((author) => {
						return author.name.replace(' ', '_') + '#' + author.discriminator === filter.value;
					});
					channelMessages = channelMessages.filter((message) => {
						return message.authorId === author.id;
					});
				} else if (filter.key === 'mentions') {
					let author = Object.values(authors).find((author) => {
						return author.name.replace(' ', '_') + '#' + author.discriminator === filter.value;
					});
					channelMessages = channelMessages.filter((message) => {
						if (!message.mentions) {
							return false;
						}
						return message.mentions.find((mention) => mention.id === author.id);
					});
				} else if (filter.key === 'pinned' && filter.value === 'true') {
					channelMessages = channelMessages.filter((message) => {
						return message.isPinned;
					});
				} else if (filter.key === 'pinned' && filter.value === 'false') {
					channelMessages = channelMessages.filter((message) => {
						return !message.isPinned;
					});
				} else if (filter.key === 'deleted' && filter.value === 'true') {
					channelMessages = channelMessages.filter((message) => {
						return message.isDeleted;
					});
				} else if (filter.key === 'deleted' && filter.value === 'false') {
					channelMessages = channelMessages.filter((message) => {
						return !message.isDeleted;
					});
				} else if (filter.key === 'has' && filter.value === 'link') {
					channelMessages = channelMessages.filter((message) => {
						return message.content.includes('http');
					});
				} else if (filter.key === 'has' && filter.value === 'embed') {
					channelMessages = channelMessages.filter((message) => {
						return message.embeds && message.embeds.length > 0;
					});
				} else if (filter.key === 'has' && filter.value === 'file') {
					channelMessages = channelMessages.filter((message) => {
						return message.attachments && message.attachments.length > 0;
					});
				} else if (filter.key === 'before') {
					let date = new Date(filter.value);
					channelMessages = channelMessages.filter((message) => {
						return new Date(message.timestamp) < date;
					});
				} else if (filter.key === 'after') {
					let date = new Date(filter.value);
					channelMessages = channelMessages.filter((message) => {
						return new Date(message.timestamp) > date;
					});
				} else if (filter.key === 'has' && filter.value === 'image') {
					channelMessages = channelMessages.filter((message) => {
						return (
							message.attachments &&
							message.attachments.some((attachment) => attachment.url.type === 'image')
						);
					});
				} else if (filter.key === 'has' && filter.value === 'video') {
					channelMessages = channelMessages.filter((message) => {
						return (
							message.attachments &&
							message.attachments.some((attachment) => attachment.url.type === 'video')
						);
					});
				} else if (filter.key === 'has' && filter.value === 'sound') {
					channelMessages = channelMessages.filter((message) => {
						return (
							message.attachments &&
							message.attachments.some((attachment) => attachment.url.type === 'audio')
						);
					});
				} else if (filter.key === 'filetype') {
					channelMessages = channelMessages.filter((message) => {
						return (
							message.attachments &&
							message.attachments.some((attachment) => attachment.url.extension === filter.value)
						);
					});

					//filename
				} else if (filter.key === 'filename') {
					channelMessages = channelMessages.filter((message) => {
						return (
							message.attachments &&
							message.attachments.some((attachment) => attachment.url.hashedFilename.includes(filter.value))  ||
							message.embeds &&
							message.embeds.some((embed) => embed.thumbnail?.url.hashedFilename.includes(filter.value))
						);
					});
				} else if (filter.key === 'reaction') {
					let emoji = Object.values(guild.emojis).find((emoji) => emoji.name === filter.value);
					channelMessages = channelMessages.filter((message) => {
						return (
							message.reactions &&
							message.reactions.some((reaction) => reaction.emojiId.includes(filter.value))
						);
					});
				} else if (filter.key === 'has' && filter.value === 'reaction') {
					channelMessages = channelMessages.filter((message) => {
						return message.reactions && message.reactions.length > 0;
					});
				} else if (filter.key === 'has' && filter.value === 'quote') {
					channelMessages = channelMessages.filter((message) => {
						return message.content.includes('>');
					});
				} else if (filter.key === 'has' && filter.value === 'code') {
					channelMessages = channelMessages.filter((message) => {
						return message.content.includes('```');
					});
				} else if (filter.key === 'has' && filter.value === 'emoji') {
					channelMessages = channelMessages.filter((message) => {
						return message.content.includes(':');
					});
				} else if (filter.key === 'has' && filter.value === 'mention') {
					channelMessages = channelMessages.filter((message) => {
						return message.mentions && message.mentions.length > 0;
					});
				} else if (filter.key === 'has' && filter.value === 'bot') {
					channelMessages = channelMessages.filter((message) => {
						return message.author && message.author.isBot;
					});
				} else if (filter.key === 'has' && filter.value === 'webhook') {
					channelMessages = channelMessages.filter((message) => {
						return message.author && message.author.isWebhook;
					});
				} else if (filter.key === 'in') {
					let channel = Object.values(guild.channels).find((channel) => {
						return channel.name.replaceAll(' ', '_') === filter.value;
					});
					channelMessages = channelMessages.filter((message) => {
						return message.channelId === channel.id;
					});
				} else if (filter.key === 'category') {
					let channelIds = Object.values(guild.categories).filter((category) => {
						return category.name.replaceAll(' ', '_') === filter.value;
					}).map((category) => Object.values(category.channelIds).map((channel) => channel.id));

					// flatten array
					channelIds = [].concat.apply([], channelIds);

					channelMessages = channelMessages.filter((message) => {
						return channelIds.includes(message.channelId) || channelIds.includes(message.categoryId);
					});
				} else if (filter.key === 'id' && filter.value) {
					let paddedId = filter.value.padStart(24, '0');
					// search based on message id
					channelMessages = channelMessages.filter((message) => {
						return message.id === paddedId;
					});
				}
			}

			found_messages_temp.push(...channelMessages);
			$searched = true;
		}

		found_messages_temp = found_messages_temp.sort((a, b) => {
			return BigInt(a.id) > BigInt(b.id) ? -1 : 1;
		});

		// add searchPrevMessage and searchNextMessage to all messages - so channel names can be displayed in search results
		for (let i = 0; i < found_messages_temp.length; i++) {
			let message = found_messages_temp[i];
			let prevMessage = found_messages_temp[i - 1];
			let nextMessage = found_messages_temp[i + 1];
			if (prevMessage) {
				message.searchPrevMessageChannelId = prevMessage.channelId;
			} else {
				message.searchPrevMessageChannelId = 'first';
			}
			if (nextMessage) {
				message.searchNextMessageChannelId = nextMessage.channelId;
			} else {
				message.searchNextMessageChannelId = 'last';
			}
		}
		console.log('found messages', found_messages_temp);

		// set found messages
		$found_messages = found_messages_temp;
		$searched = true;
	}
</script>

<div class="search">
	<div class="search-input-container">
		<input
			type="text"
			placeholder="Search in guild"
			bind:value
			bind:this={input}
			on:focus={() => {
				inputValueChanged(value);
				isInputFocused = true;
			}}
			on:blur={() => (unfocusTimeout = setTimeout(() => (isInputFocused = false), 100))}
			on:keydown={(e) => {
				inputValueChanged(value);

				if (e.key === 'ArrowDown') {
					selectedMenuIndex++;
					e.preventDefault();
				} else if (e.key === 'ArrowUp') {
					selectedMenuIndex--;
					e.preventDefault();
				}
				// if enter
				else if (e.key === 'Enter') {
					e.target.blur()
					findMessages()
				}
			}}
			on:input={() => inputValueChanged(value)}
		/>
		<button on:click={findMessages} id="search-submit-btn">Search</button>
	</div>

	{#if isInputFocused}
		<div class="search-options">
			{#if 'key' in parsedCursorHere && (parsedCursorHere.key === 'from' || parsedCursorHere.key === 'mentions')}
				{#each filterAuthors(authors, value) as author, i}
					{#key author.id}
						<div
							class="author search-option"
							on:click={() =>
								selectOptionValue(author.name.replaceAll(' ', '_') + '#' + author.discriminator)}
						>
							<img class="avatar" src={checkUrl(author?.avatarUrl?.url)} alt="Avatar" loading="lazy" />
							<div>{author.nickname} ({author.name}#{author.discriminator})</div>
							<div class="spacer"></div>
							<div>{author.messagesCount}x</div>
						</div>
					{/key}
				{/each}
			{:else if 'key' in parsedCursorHere && parsedCursorHere.key === 'in' && value.length > 0}
				{#each filterChannels(guild.channels, value) as channel, i}
					{#key channel.id}
						<div
							class="channel search-option"
							on:click={() => selectOptionValue(channel.name.replaceAll(' ', '_'))}
						>
							# {channel.name}
							<div>({channel.messageCount}x)</div>
						</div>
					{/key}
				{/each}
			{:else if 'key' in parsedCursorHere && parsedCursorHere.key === 'category' && value.length > 0}
				{#each filterChannels(guild.categories, value) as category, i}
					{#key category.id}
						<div
							class="channel search-option"
							on:click={() => selectOptionValue(category.name.replaceAll(' ', '_'))}
						>
							# {category.name}
						</div>
					{/key}
				{/each}
			{:else if 'key' in parsedCursorHere && parsedCursorHere.key === 'reaction' && value.length > 0}
				<div class="emoji-search-container">
				{#each filterEmojis(guild.emojis, value) as emoji, i}
					{#key emoji.name}
						<div
							class="emoji search-option"
							on:click={() => selectOptionValue(emoji.name)}
						>
							<img class="emoji" src={checkUrl(emoji?.imageUrl?.url)} alt={":" + emoji.name + ":"} loading="lazy" width="30" height="30" title={emoji.name+" (" + emoji.usedCount + "x)"} />
						</div>
					{/key}
				{/each}
				</div>
			{:else if 'key' in parsedCursorHere && parsedCursorHere.key === 'filetype' && value.length > 0}
				<div class="emoji-search-container">
				{#each filterFiletypes(guild.extensions, value) as extension, i}
					{#key extension}
						<div
							class="filetype search-option"
							on:click={() => selectOptionValue(extension)}
						>
							{extension}
						</div>
					{/key}
				{/each}
				</div>
			{:else}
				<div>
					{#if filterKeys('from:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectOptionKey('from')}>
							<b>from: </b>user
						</div>
					{/if}
					{#if filterKeys('mentions:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectOptionKey('mentions')}>
							<b>mentions: </b>user
						</div>
					{/if}
					{#if filterKeys('has:link', parsedCursorHere)}
						<div class="search-option" on:click={() => selectFullOption('has', 'link')}>
							<b>has: </b>link
						</div>
					{/if}
					{#if filterKeys('has:embed', parsedCursorHere)}
						<div class="search-option" on:click={() => selectFullOption('has', 'embed')}>
							<b>has: </b>embed
						</div>
					{/if}
					{#if filterKeys('has:file', parsedCursorHere)}
						<div class="search-option" on:click={() => selectFullOption('has', 'file')}>
							<b>has: </b>file
						</div>
					{/if}
					{#if filterKeys('has:image', parsedCursorHere)}
						<div class="search-option" on:click={() => selectFullOption('has', 'image')}>
							<b>has: </b>image
						</div>
					{/if}
					{#if filterKeys('has:video', parsedCursorHere)}
						<div class="search-option" on:click={() => selectFullOption('has', 'video')}>
							<b>has: </b>video
						</div>
					{/if}
					{#if filterKeys('has:sound', parsedCursorHere)}
						<div class="search-option" on:click={() => selectFullOption('has', 'sound')}>
							<b>has: </b>sound
						</div>
					{/if}
					{#if filterKeys('before:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectOptionKey('before')}>
							<b>before: </b>specific date
						</div>
					{/if}
					{#if filterKeys('reaction:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectOptionKey('reaction')}>
							<b>reaction: </b>emoji
						</div>
					{/if}
					{#if filterKeys('filetype:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectOptionKey('filetype')}>
							<b>filetype: </b>extension
						</div>
					{/if}
					{#if filterKeys('filename:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectOptionKey('filename')}>
							<b>filename: </b>name
						</div>
					{/if}
					<!-- {#if filterKeys('during:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectOptionKey('during')}>
							<b>[WIP] during: </b>specific date
						</div>
					{/if} -->
					{#if filterKeys('after:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectOptionKey('after')}>
							<b>after: </b>specific date
						</div>
					{/if}
					{#if filterKeys('in:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectOptionKey('in')}>
							<b>in: </b>channel
						</div>
					{/if}
					{#if filterKeys('category:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectOptionKey('category')}>
							<b>category: </b>category name
						</div>
					{/if}
					{#if filterKeys('pinned:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectFullOption('pinned', 'true')}>
							<b>pinned: </b>true
						</div>
					{/if}
					{#if filterKeys('pinned:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectFullOption('pinned', 'false')}>
							<b>pinned: </b>false
						</div>
					{/if}
					{#if filterKeys('deleted:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectFullOption('deleted', 'true')}>
							<b>deleted: </b>true
						</div>
					{/if}
					{#if filterKeys('deleted:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectFullOption('deleted', 'false')}>
							<b>deleted: </b>false
						</div>
					{/if}
					{#if filterKeys('id:', parsedCursorHere)}
						<div class="search-option" on:click={() => selectOptionKey('id')}>
							<b>id: </b>message id
						</div>
					{/if}
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.spacer {
		width: 100%;
	}
	input {
		/* width: 100%; */
		width: 250px;
		background-color: #202225;
		color: white;
		height: 25px;
		border: 0px;
		border-radius: 3px;
	}
	input::placeholder {
		color: #909297;
	}
	.search {
		position: relative;
		background-color: #2f3136;
	}
	.search-options {
		background-color: #18191c;
		border-radius: 5px;
		padding: 2px 5px;
		max-width: 700px;
		min-width: 500px;

		position: absolute;
		top: 50px;
		right: 50px;

		z-index: 100;
		max-height: 70vh;
		overflow-y: auto;
	}
	.search-option {
		padding: 5px 5px;
		margin: 5px 10px;
		border-radius: 5px;
	}

	.search-option:hover {
		background-color: #2f3136;
	}

	.author {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 15px;
		margin: 15px 30px;
	}
	.avatar {
		width: 30px;
		height: 30px;
		border-radius: 50%;
	}
	.search-input-container {
		display: flex;
		align-items: center;
		/* gap: 15px; */
		/* margin: 15px 30px; */
	}

	#search-submit-btn {
		height: 100%;
		background: none;
		border: none;
		background-color: #DCDDDE;
		color: #18191c;
		cursor: pointer;
		padding: 5px 10px;
		/* width: 60px; */
	}

	.emoji-search-container {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
	}

	.channel{
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 15px;
		/* margin: 5px 30px; */
	}
</style>
