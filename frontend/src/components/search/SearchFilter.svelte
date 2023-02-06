<script lang="ts">
	import { searchResultsMessageIds, searchShown } from "./searchStores";
	export let guildId: string;

	// input
	let domInput: HTMLInputElement;
	let isInputFocused = false;
	let inputValue = '';
	let searchKey = '';
	let searchValue = null;
	let selectedMenuIndex = -1;
	let unfocusTimeout;

	function inputOnKeyDown(e: KeyboardEvent) {
		if (e.key === 'ArrowDown') {
			selectedMenuIndex++;
			e.preventDefault();
		} else if (e.key === 'ArrowUp') {
			selectedMenuIndex--;
			e.preventDefault();
		}
		// if enter
		else if (e.key === 'Enter') {
			if (selectedMenuIndex > -1) {
				let categoryKey = filteredCategories[selectedMenuIndex].key;
				replaceLastWord(categoryKey + ':')
				console.log("todo: select menu item");
				selectedMenuIndex = -1;
			}
			else {
				domInput.blur();
				inputOnSubmit();
			}
		}
	}

	function inputOnFocus() {
		inputValueChanged(inputValue);
		isInputFocused = true;
	}
	function inputOnBlur() {
		unfocusTimeout = setTimeout(() => (isInputFocused = false), 100);
	}


	function getSearchKeyValue(inputValue: string): { key: string , value: string | null } {
		let key = "";
		let value = null;

		// get last word
		let lastWord = inputValue.split(' ').pop();
		// console.log('last word', lastWord);

		if (lastWord === undefined) {
			// console.log('no last word');
			return { key, value };
		}
		else if (lastWord.includes(':')) {
			[key, value] = lastWord.split(':');
		}
		else {
			key = lastWord;
		}

		return { key, value };
	}

	function replaceLastWord(newWord: string): void {
		let words = inputValue.split(' ');
		words.pop();
		words.push(newWord);
		inputValue = words.join(' ');

		domInput.focus();
		isInputFocused = true;
	}

	interface FilterCategory {
		key: string;
		description: string;
		type: 'string' | 'discord_snowflake' | 'number' | 'boolean';
	}

	let categories: FilterCategory[] = [
		{
			key: 'message_id',
			description: 'id',
			type: 'discord_snowflake'
		},
		{
			key: 'user_id',
			description: 'id',
			type: 'discord_snowflake',
		},
		{
			key: 'user',
			description: 'string',
			type: 'string',
		},
		{
			key: 'mentions_user_id',
			description: 'id',
			type: 'discord_snowflake',
		},
		{
			key: 'mentions_user',
			description: 'string',
			type: 'string',
		},
		{
			key: 'reaction_id',
			description: 'id',
			type: 'discord_snowflake',
		},
		{
			key: 'reaction',
			description: 'string',
			type: 'string',
		},
		{
			key: 'extension',
			description: 'pdf/png/jpg/etc',
			type: 'string',
		},
		{
			key: 'filename',
			description: 'string',
			type: 'string',
		},
		{
			key: 'in_channel_id',
			description: 'id',
			type: 'discord_snowflake',
		},
		{
			key: 'in_category_id',
			description: 'id',
			type: 'discord_snowflake',
		},
		{
			key: 'is_pinned',
			description: 'true/false',
			type: 'boolean',
		},
		{
			key: 'has_audio',
			description: 'true/false',
			type: 'boolean',
		},
		{
			key: 'has_image',
			description: 'true/false',
			type: 'boolean',
		},
		{
			key: 'has_video',
			description: 'true/false',
			type: 'boolean',
		},
		{
			key: 'has_other',
			description: 'true/false',
			type: 'boolean',
		},
		{
			key: 'has_link',
			description: 'true/false',
			type: 'boolean',
		},
		{
			key: 'is_edited',
			description: 'true/false',
			type: 'boolean',
		},
		{
			key: 'limit',
			description: 'number (default 100000)',
			type: 'number',
		},
	]

	let filteredCategories: FilterCategory[] = [];
	function filterOptions(newValue: string) {
		let { key, value } = getSearchKeyValue(newValue);
		searchKey = key;
		searchValue = value;
		// console.log('key', key, 'value', value);

		if (value === null) {
			filteredCategories = categories.filter((category) => {
				return category.key.includes(key);
			});
		}
		else {
			filteredCategories = [];
		}
	}

	function inputValueChanged() {
		filterOptions(inputValue);
	}

	async function inputOnSubmit() {
		// do a fetch to the server to search for the message

		let query = inputValue;
		let response = await fetch(`/api/search?guild_id=${guildId}&prompt=${query}`);
		let json = await response.json();
		$searchResultsMessageIds = json;
		$searchShown = true;
	}

	// $: console.log('selectedMenuIndex', selectedMenuIndex);
	// $: console.log('inputValue', inputValue);
</script>

<div class="search">
	<div class="search-input-container">
		<input
			type="text"
			placeholder="Search in guild"
			bind:value={inputValue}
			bind:this={domInput}
			on:focus={inputOnFocus}
			on:blur={inputOnBlur}
			on:keydown={inputOnKeyDown}
			on:input={inputValueChanged}
		/>
		<button on:click={inputOnSubmit} id="search-submit-btn">Search</button>
	</div>

	{#if isInputFocused}
		<div class="search-options">
			
			{#if searchValue === null}
				{#if filteredCategories.length > 0}
					{#each filteredCategories as category, i}
						{#key category}
							<div
								class="search-option" class:active={selectedMenuIndex === i}
								on:click={() => replaceLastWord(category.key + ':')}
							>
								<b>{category.key}: </b>{category.description}
								
							</div>
						{/key}
					{/each}
				{/if}
			{:else}
				{@const category = categories.find(c => c.key === searchKey)}
				{#if category && category.type == 'boolean'}
					{#each ['true', 'false'] as option, i}
						{#key option}
							<div
								class="search-option" class:active={selectedMenuIndex === i}
								on:click={() => replaceLastWord(option)}
							>
								<b>{option}</b>
							</div>
						{/key}
					{/each}
				{/if}
			{/if}
		</div>
	{/if}
</div>

<style>

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

	.search-option:hover,
	.search-option.active {
		background-color: #2f3136;
	}
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
		background-color: #dcddde;
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

	.channel {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 15px;
		/* margin: 5px 30px; */
	}
</style>
