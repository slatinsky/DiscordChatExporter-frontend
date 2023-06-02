<script lang="ts">
	import { onMount } from "svelte";

	interface SearchCategory {
		key: string;
		description: string;
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


	import { searchPrompt, searchResultsMessageIds, searchShown } from "./searchStores";
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
				inputOnSubmit();
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
					action: () => {
						console.log("accept suggestion", category.key);
						// $searchPrompt = $searchPrompt.replace(key, category.key + ':');
						$searchPrompt = $searchPrompt.replace(new RegExp(`${key}$`), `${category.key}:`);
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
							}
						},
						{
							key: "false",
							description: "",
							action: () => {
								$searchPrompt = $searchPrompt.replace(new RegExp(`:"?${value}$`), ":false ");
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
						let response = await fetch(`/api/search-autocomplete?guild_id=${encodeURIComponent(guildId)}&key=${encodeURIComponent(searchCategory.autocompleteApi)}&value=${encodeURIComponent(value)}`);
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

	async function inputOnSubmit() {
		// do a fetch to the server to search for the message

		let query = $searchPrompt;
		let response = await fetch(`/api/search?guild_id=${encodeURIComponent(guildId)}&prompt=${encodeURIComponent(query)}`);
		let json = await response.json();
		$searchResultsMessageIds = json;
		$searchShown = true;
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
		focusInput()
	}

	function searchSuggestionsChanged() {
		selectedMenuIndex = -1;
	}

	$: searchSuggestions, searchSuggestionsChanged();
	$: $searchPrompt, searchPromptChanged()


	onMount(async () => {
		searchCategories = await fetchCategories()
	})
</script>

<div class="search">
	<div class="search-input-container">
		<input
			type="text"
			placeholder="Search in guild"
			bind:value={$searchPrompt}
			bind:this={domInput}
			on:focus={inputOnFocus}
			on:blur={inputOnBlur}
			on:keydown={inputOnKeyDown}
			on:input={searchPromptChanged}
		/>
		<button on:click={inputOnSubmit} id="search-submit-btn">Search</button>
	</div>

	{#if isInputFocused && searchSuggestions.length > 0}
		<div class="search-options">
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

	.search-option-inner {
		display: flex;
		gap: 15px;
	}
</style>
