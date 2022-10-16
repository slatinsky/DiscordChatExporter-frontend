<script>
	export let authors;
	export let all_messages;
	export let guildId;

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


	let found_messages = [];
	function findMessages() {
		console.log('searching for messages');
		found_messages = [];
		let limit = 100;

		console.log(all_messages);

		console.log('--', Object.keys(all_messages).length, 'messages to search through');

		for (const [channelId, channel] of Object.entries(all_messages)) {
			let channelMessages = Object.values(channel);

			for (const filter of filters) {
				if (filter.content) {
					channelMessages = channelMessages.filter((message) => {
						return normalizeSearchTerm(message.content).includes(
							normalizeSearchTerm(filter.content)
						);
					});
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
						return message.attachments && message.attachments.length > 0;
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
				}
				// else if (filter.key === 'in') {
				//     let channel = Object.values(channels).find((channel) => {
				//         return channel.name === filter.value
				//     })
				//     channelMessages = channelMessages.filter((message) => {
				//         return message.channelId === channel.id
				//     });
				// }
			}

			found_messages.push(...channelMessages);

		}
		console.log('found messages', found_messages);
	}
</script>

isInputFocused: {isInputFocused} <br />
cursorPosition: {cursorPosition} <br />

<div class="search">
	<input
		type="text"
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
		}}
		on:input={() => inputValueChanged(value)}
	/>
	<button on:click={findMessages}>Find</button>

	{#if isInputFocused}
		<div class="search-options">
			{#if 'key' in parsedCursorHere && (parsedCursorHere.key === 'from' || parsedCursorHere.key === 'mentions')}
				{#each filterAuthors(authors, value) as author, i}
					{#key author.id}
						<div
							class="author search-option"
							on:click={() =>
								selectOptionValue(author.name.replace(' ', '_') + '#' + author.discriminator)}
						>
							<img class="avatar" src={author?.localFilePath} alt="Avatar" loading="lazy" />
							<div>{author.nickname} ({author.name}#{author.discriminator})</div>
						</div>
					{/key}
				{/each}
			{:else}
				<div>
					{#if !value.includes('from:')}
						<div class="search-option" on:click={() => selectOptionKey('from')}>
							<b>from: </b>user
						</div>
					{/if}
					{#if !value.includes('mentions:')}
						<div class="search-option" on:click={() => selectOptionKey('mentions')}>
							<b>mentions: </b>user
						</div>
					{/if}
					{#if !value.includes('has:link')}
						<div class="search-option" on:click={() => selectFullOption('has', 'link')}>
							<b>has: </b>link
						</div>
					{/if}
					{#if !value.includes('has:embed')}
						<div class="search-option" on:click={() => selectFullOption('has', 'embed')}>
							<b>has: </b>embed
						</div>
					{/if}
					{#if !value.includes('has:file')}
						<div class="search-option" on:click={() => selectFullOption('has', 'file')}>
							<b>has: </b>file
						</div>
					{/if}
					{#if !value.includes('before:')}
						<div class="search-option" on:click={() => selectOptionKey('before')}>
							<b>before: </b>specific date
						</div>
					{/if}
					{#if !value.includes('during:')}
						<div class="search-option" on:click={() => selectOptionKey('during')}>
							<b>[WIP] during: </b>specific date
						</div>
					{/if}
					{#if !value.includes('after:')}
						<div class="search-option" on:click={() => selectOptionKey('after')}>
							<b>after: </b>specific date
						</div>
					{/if}
					{#if !value.includes('in:')}
						<div class="search-option" on:click={() => selectOptionKey('in')}>
							<b>[WIP] in: </b>channel
						</div>
					{/if}
					{#if !value.includes('pinned:')}
						<div class="search-option" on:click={() => selectFullOption('pinned', 'true')}>
							<b>pinned: </b>true
						</div>
					{/if}
					{#if !value.includes('pinned:')}
						<div class="search-option" on:click={() => selectFullOption('pinned', 'false')}>
							<b>pinned: </b>false
						</div>
					{/if}
				</div>
			{/if}
		</div>
	{/if}
</div>

{#each found_messages as message}
	<!-- <pre>{JSON.stringify(message, null, 2)}</pre> -->
	<div>
		<a href="/channels/{guildId}/{message.channelId}#{message.id}" target="_blank">
			{message.content}</a
		>
	</div>
{/each}

<style>
	input {
		width: 100%;
		max-width: 500px;
	}
	.search {
		position: relative;
	}
	.search-options {
		background-color: #18191c;
		border-radius: 5px;
		padding: 2px 5px;
		max-width: 500px;
		min-width: 300px;

		position: absolute;
		top: 50px;
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
		gap: 15px;
		margin: 15px 30px;
	}
	.avatar {
		width: 30px;
		height: 30px;
		border-radius: 50%;
	}
</style>
