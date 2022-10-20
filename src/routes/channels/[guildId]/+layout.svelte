<script>
	import Header from './Header.svelte';
	import SearchResults from './SearchResults.svelte';
	import { searched, found_messages } from './searchStores';
	export let data;

	$: console.warn('found_messages', found_messages);
	$: console.warn('searched', searched);

	let currentGuildId = data.guildId;
	function guildChanged(_) {  // fix crash if shifting between guilds and searching at the same time
		if (currentGuildId !== data.guildId) {
			currentGuildId = data.guildId;
			$found_messages = [];
			$searched = false;
		}
		console.log('current guild', data.guild);
	}
	$: guildChanged(data);
</script>

<div id="guild-layout" class={$searched ? 'with-search' : ''}>
	<div id="channels">
		<div class="guild-name">{data.guilds[data.guildId].name}</div>
		{#each Object.values(data.guild.categories) as category}
			<div class="category">{category.name}</div>
			{#each category.channelIds as channel}
				<div class="channel">
					<a
						href="/channels/{data.guildId}/{channel.id}"
						class={data.channelId == channel.id ? 'selected' : ''}># {channel.name}</a
					>
					{#if channel.threads}
						{#each channel.threads as thread}
							<div>
								<div class="thread" title={thread.name}>
									<!-- {thread.id} -->
									<a
										href="/channels/{data.guildId}/{thread.id}"
										class={data.channelId == thread.id ? 'selected' : ''}
									>
										<!-- svg -->
										<svg
											class="thread-svg-icon"
											width="8"
											height="8"
											viewBox="0 0 12 11"
											fill="none"
											aria-hidden="true"
											><path
												d="M11 9H4C2.89543 9 2 8.10457 2 7V1C2 0.447715 1.55228 0 1 0C0.447715 0 0 0.447715 0 1V7C0 9.20914 1.79086 11 4 11H11C11.5523 11 12 10.5523 12 10C12 9.44771 11.5523 9 11 9Z"
												fill="currentColor"
											/></svg
										>
										{thread.name}</a
									>
								</div>
							</div>
						{/each}
					{/if}
				</div>
			{/each}
		{/each}
	</div>
	<div id="header">
		{#key data.channelId}
			<Header
				guild={data.guild}
				channel={data.guild.channels[data.channelId]}
				messages={data.messages}
			/>
		{/key}
	</div>
	<div id="messages">
		<slot />
	</div>
	{#if $searched}
		<div id="search">
			<SearchResults guild={data.guild} />
		</div>
	{/if}
</div>

<style>
	#guild-layout {
		display: grid;
		/* flex-direction: row; */
		background-color: #2f3136;
		height: 100vh;

		grid-template-areas:
			'channels header header'
			'channels messages messages';

		grid-template-columns: 250px 3fr 2fr;
		grid-template-rows: 50px auto;
	}

	#guild-layout.with-search {
		grid-template-areas:
			'channels header header'
			'channels messages search';
	}

	#channels {
		grid-area: channels;
		display: flex;
		flex-direction: column;
		padding: 0 15px 10px 15px;
		margin-right: 5px;
		overflow-y: auto;
	}
	#channels .guild-name {
		padding: 10px 0 10px 0;
		font-size: 20px;
		font-weight: 600;
		position: sticky;
		top: 0;
		background-color: #2f3136;
		border-bottom: 2px solid #202225;
		margin-bottom: 10px;
	}
	#channels .channel {
		margin: 5px 15px;
	}
	#channels .channel > a {
		/* color: #b9bbbe; */
		/* color: white !important; */
		color: #dcddde;
	}
	#channels .selected {
		color: chartreuse !important;
	}
	#channels .category {
		padding-top: 15px;
		font-size: 0.9rem;
		text-transform: uppercase;
	}
	#channels .category-name {
		font-size: 16px;
		font-weight: 600;
		margin: 15px 0 0px 0;
	}
	#channels .thread {
		margin: 5px 15px 5px 30px;
		font-size: small;

		text-decoration: none;
		display: -webkit-box;
		-webkit-line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
	#channels .thread > a {
		color: gray;
	}
	#channels .thread:hover {
		color: white;
	}

	#header {
		grid-area: header;
	}

	#messages {
		grid-area: messages;
	}

	#search {
		grid-area: search;
	}
	#search:empty {
		display: none;
	}
</style>
