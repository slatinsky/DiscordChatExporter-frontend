<script lang="ts">
	import { onMount } from "svelte";

	interface SearchCategory {
		key: string;
		description: string;
		description2?: string;
		type: 'string' | 'discord_snowflake' | 'number' | 'boolean';
		multiple: boolean;
		mapTo: string;
		autocompleteApi: string | null  // mapTo - useful only on the backend
	}
	interface SearchSuggestion {
		key: string;
		description: string;
		action: () => void;
	}


	import { searchPrompt, searchPromptLarge, searchResultsMessageIds, searchShown, submitSearch } from "./searchStores";
	import { checkUrl } from "src/js/helpers";
	export let guildId: string;

	let searchCategories: SearchCategory[] = []

	async function fetchCategories(): Promise<SearchCategory> {
		const res = await fetch('/api/search-categories')
		const json = await res.json()
		return json
	}




	// input
	let domInput: HTMLInputElement;
	let searchSuggestionDoms: HTMLDivElement[] = [];
	let isInputFocused = false;

	let selectedMenuIndex = -1;


	function parsePrompt(prompt: string) {
		let insideQuotes = false;
		let validSearchCategoriesKeys = searchCategories.map((category) => category.key);

		let foundKeys: string[] = [];
		let key = '';
		let value = '';

		let state: 'key' | 'value' = 'key';

		for (let i = 0; i < prompt.length; i++) {
			let char = prompt[i];
			if (char === '"') {
				insideQuotes = !insideQuotes;
				continue
			}
			if (char === ':' && !insideQuotes && validSearchCategoriesKeys.includes(key)) {
				state = 'value';
				foundKeys.push(key);
				continue
			}
			if (char === ' ' && !insideQuotes) {
				state = 'key';
				key = '';
				value = '';
				continue
			}

			if (state === 'key') {
				key += char;
			}
			else if (state === 'value') {
				value += char;
			}
		}

		return { key, value, state, foundKeys }
	}

	function scrollToSuggestion(index: number) {
		if (index >= 0 && index < searchSuggestions.length) {
			searchSuggestionDoms[index].scrollIntoView({ behavior: "smooth", block: "nearest" });
		}
	}


	function inputOnKeyDown(e: KeyboardEvent) {
		if (e.key === 'ArrowDown') {
			selectedMenuIndex++;
			if (selectedMenuIndex >= searchSuggestions.length) {
				selectedMenuIndex = -1;
			}
			scrollToSuggestion(selectedMenuIndex)
			e.preventDefault();
		} else if (e.key === 'ArrowUp') {
			selectedMenuIndex--;
			if (selectedMenuIndex < -1) {
				selectedMenuIndex = searchSuggestions.length - 1;
			}
			scrollToSuggestion(selectedMenuIndex)
			e.preventDefault();
		}
		// if enter
		else if (e.key === 'Enter') {
			if (selectedMenuIndex > -1) {
				searchSuggestions[selectedMenuIndex].action();
				selectedMenuIndex = -1;
				e.preventDefault();
			}
			else {
				domInput.blur();
				submitSearch(guildId);
			}
		}
	}


	let searchSuggestions: SearchSuggestion[] = []
	function searchPromptChanged() {
		const validSearchCategoriesKeys = searchCategories.map((category) => category.key);
		const singleOnlySearchCategoriesKeys = searchCategories.filter((category) => !category.multiple).map((category) => category.key);

		const { key, value, state, foundKeys } = parsePrompt($searchPrompt);
		const usedSingleKeys = foundKeys.filter((key) => {
			return singleOnlySearchCategoriesKeys.includes(key);
		});

		console.log('key', key, 'value', value, 'state', state, 'foundKeys', foundKeys, 'singleKeys', usedSingleKeys);

		if (state === 'key') {
			searchSuggestions = searchCategories.filter((category) => {
				return category.key.includes(key) && !usedSingleKeys.includes(category.key);
			}).map((category) => {
				return {
					key: category.key,
					description: category.description,
					description2: category?.description2 ?? undefined,
					action: () => {
						console.log("accept suggestion", category.key);
						// $searchPrompt = $searchPrompt.replace(key, category.key + ':');
						$searchPrompt = $searchPrompt.replace(new RegExp(`${key}$`), `${category.key}:`);
						focusInput()
					}
				}
			});
			console.log('searchSuggestions', searchSuggestions);
		}
		else if (key !== '' && validSearchCategoriesKeys.includes(key)) {
				const searchCategory = searchCategories.find((category) => category.key === key);
				if (searchCategory?.type === "boolean") {
					searchSuggestions = [
						{
							key: "true",
							description: "",
							action: () => {
								$searchPrompt = $searchPrompt.replace(new RegExp(`:"?${value}$`), ":true ");
								submitSearch(guildId);
							}
						},
						{
							key: "false",
							description: "",
							action: () => {
								$searchPrompt = $searchPrompt.replace(new RegExp(`:"?${value}$`), ":false ");
								submitSearch(guildId);
							}
						}
					].filter((suggestion) => {
						return suggestion.key.includes(value);
					});
				}
				else if (searchCategory.autocompleteApi !== null) {
					searchSuggestions = [];
					// do a fetch to the server to search for the message
					(async () => {
						let query = $searchPrompt;
						let response = await fetch(`/api/guild/search/autocomplete?guild_id=${encodeURIComponent(guildId)}&key=${encodeURIComponent(searchCategory.autocompleteApi)}&value=${encodeURIComponent(value)}`);
						let json = await response.json();
						console.log('json', json);
						
						if (json.type !== "unknown_key") {
							searchSuggestions = json.map((suggestion) => {
							if (suggestion.key.includes(" ")) {
								suggestion.key = `"${suggestion.key}"`;
							}
							return {
									key: suggestion.key,
									description: suggestion.description,
									description2: suggestion?.description2 ?? undefined,
									icon: suggestion?.icon ?? undefined,
									action: () => {
										$searchPrompt = $searchPrompt.replace(new RegExp(`:"?${value}$`), `:${suggestion.key} `);
										submitSearch(guildId);
									}
								}
							});
						}
					})();
				}
				else {
					searchSuggestions = [];
				}
			}
		else {
			searchSuggestions = [];
		}
	}




	let unfocusTimeout: NodeJS.Timeout;
	function inputOnFocus() {
		isInputFocused = true;
		clearTimeout(unfocusTimeout);
		searchPromptChanged()
	}
	function inputOnBlur() {
		unfocusTimeout = setTimeout(() => (isInputFocused = false), 100);
	}
	function focusInput() {
		domInput.focus();
		isInputFocused = true;
		clearTimeout(unfocusTimeout);
	}

	function onClickSuggestion(suggestionAction: () => void) {
		suggestionAction();
	}

	function searchSuggestionsChanged() {
		selectedMenuIndex = -1;
	}

	$: searchSuggestions, searchSuggestionsChanged();
	$: $searchPrompt, searchPromptChanged()

	$: $searchPromptLarge = $searchPrompt !== '' || $searchShown || isInputFocused;


	function clearSearch() {
		$searchPrompt = ''
	}

	$: if ($searchPrompt === '') {
		$searchShown = false;
	}


	onMount(async () => {
		searchCategories = await fetchCategories()
	})
</script>

<div class="search" class:large={$searchPromptLarge}>
	<svg on:click={()=>domInput.focus()} class="icon-magnifying-glass-mobile" aria-hidden="true" role="img" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M21.707 20.293L16.314 14.9C17.403 13.504 18 11.799 18 10C18 7.863 17.167 5.854 15.656 4.344C14.146 2.832 12.137 2 10 2C7.863 2 5.854 2.832 4.344 4.344C2.833 5.854 2 7.863 2 10C2 12.137 2.833 14.146 4.344 15.656C5.854 17.168 7.863 18 10 18C11.799 18 13.504 17.404 14.9 16.314L20.293 21.706L21.707 20.293ZM10 16C8.397 16 6.891 15.376 5.758 14.243C4.624 13.11 4 11.603 4 10C4 8.398 4.624 6.891 5.758 5.758C6.891 4.624 8.397 4 10 4C11.603 4 13.109 4.624 14.242 5.758C15.376 6.891 16 8.398 16 10C16 11.603 15.376 13.11 14.242 14.243C13.109 15.376 11.603 16 10 16Z"></path></svg>
	<div class="search-input-container">
		<input
			type="text"
			placeholder="Search"
			bind:value={$searchPrompt}
			bind:this={domInput}
			on:focus={inputOnFocus}
			on:blur={inputOnBlur}
			on:keydown={inputOnKeyDown}
			on:input={searchPromptChanged}
		/>
		<svg class:hidden={$searchPrompt !== ''} class="icon-magnifying-glass" aria-hidden="true" role="img" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M21.707 20.293L16.314 14.9C17.403 13.504 18 11.799 18 10C18 7.863 17.167 5.854 15.656 4.344C14.146 2.832 12.137 2 10 2C7.863 2 5.854 2.832 4.344 4.344C2.833 5.854 2 7.863 2 10C2 12.137 2.833 14.146 4.344 15.656C5.854 17.168 7.863 18 10 18C11.799 18 13.504 17.404 14.9 16.314L20.293 21.706L21.707 20.293ZM10 16C8.397 16 6.891 15.376 5.758 14.243C4.624 13.11 4 11.603 4 10C4 8.398 4.624 6.891 5.758 5.758C6.891 4.624 8.397 4 10 4C11.603 4 13.109 4.624 14.242 5.758C15.376 6.891 16 8.398 16 10C16 11.603 15.376 13.11 14.242 14.243C13.109 15.376 11.603 16 10 16Z"></path></svg>
		<svg class:hidden={$searchPrompt == ''} on:click={clearSearch} aria-hidden="true" role="img" class="icon-clear" width="24" height="24" viewBox="0 0 24 24"><path fill="currentColor" d="M18.4 4L12 10.4L5.6 4L4 5.6L10.4 12L4 18.4L5.6 20L12 13.6L18.4 20L20 18.4L13.6 12L20 5.6L18.4 4Z"></path></svg>
	</div>

	{#if isInputFocused && searchSuggestions.length > 0}
		<div id="search-options">
			{#each searchSuggestions as suggestion, i}
				{#key suggestion}
					<div
						class="search-option" class:active={selectedMenuIndex === i}
						on:click|stopPropagation|capture={()=>onClickSuggestion(suggestion.action)} bind:this={searchSuggestionDoms[i]}
					>
						<div class="search-option-inner">
							{#if suggestion.icon}
								<img
									class=""
									src={checkUrl(suggestion.icon)}
									alt="Avatar"
									loading="lazy"
									width="48"
									height="48"
									onerror="this.style.visibility='hidden'"
								/>
							{/if}
							<div>
								{#if suggestion.description !== ""}
									<b>{suggestion.key}:</b> {suggestion.description}
								{:else}
									<b>{suggestion.key}</b>
								{/if}
	
								{#if suggestion.description2}
									<div>
										<small>{suggestion.description2}</small>
									</div>
								{/if}
							</div>
						</div>
					</div>
				{/key}
			{/each}
		</div>
		{/if}
</div>

<style>

	#search-options {
		background-color: #111214;
		border-radius: 5px;
		padding: 2px 5px;
		max-width: 90vw;
		width: 700px;

		position: absolute;
		top: 50px;
		right: 0px;

		z-index: 1000;
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
		width: 140px;
		background-color: #202225;
		color: white;
		height: 25px;
		border: 0px;
		border-radius: 3px;
		padding: 0px 10px;
		outline: none;
	}
	input::placeholder {
		color: #909297;
	}

	input:focus,
	.large input {
		width: 250px;
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

	.search-option-inner {
		display: flex;
		gap: 15px;
	}

	.icon-magnifying-glass,
	.icon-clear {
		color: #949ba4;
		width: 16px;
		height: 16px;
		position: absolute;
		right: 5px;
	}

	.icon-clear {
		cursor: pointer;
	}

	.hidden {
		display: none;
	}

	.icon-magnifying-glass-mobile {
		display: none;
	}
	@media (max-width: 1000px) {
		.icon-magnifying-glass-mobile {
			display: block;
			cursor: pointer;
			background-color: #36393F;
		}

		.large .icon-magnifying-glass-mobile {
			display: none;
		}

		.search-input-container {
			position: fixed;
			left: -9999px;
		}

		.large .search-input-container {
			visibility: visible;
			position: relative;
			left: 0px;
		}

		.large.search {
			width: 100%;
		}
		.large.search input {
			width: 100%;
		}
	}
</style>
