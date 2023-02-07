<script lang="ts">
	import Header from './Header.svelte';
	import SearchResults from '../../../components/search/SearchResults.svelte';
	import { searchShown, searchResultsMessageIds } from '../../../components/search/searchStores';

	import type { PageServerData } from './$types';
	export let data: PageServerData;

	import ChannelsMenu from '../../../components/channels/MenuCategories.svelte';
	import Container from 'src/components/containers/Container.svelte';

	let currentGuildId: string = data.guildId;
	function guildChanged(_) {  // fix crash if shifting between guilds and searching at the same time
		if (currentGuildId !== data.guildId) {
			currentGuildId = data.guildId;
			$searchResultsMessageIds = [];
			$searchShown = false;
		}
		console.log('current guild', data.guild);
	}
	$: guildChanged(data);
</script>


{#key currentGuildId}
	{#if !data.guild}
		<Container>
			<div class="txt">Guild ID {currentGuildId} not found</div>
		</Container>
	{:else}
		<div id="guild-layout" class={$searchShown ? 'with-search' : ''}>
			<div id="channels">
				<div class="guild-name">{data.guild.name}</div>
				<ChannelsMenu selectedGuildId={data.guildId} channels={data.channels} selectedChannelId={data.channelId} />
			</div>
			<div id="header">
				{#key data.channelId}
					<Header channel={data.channel} thread={data.thread} guildId={data.guildId} />
				{/key}
			</div>
			<div id="messages">
				<slot />
			</div>
			{#if $searchShown}
				<div id="search">
					<SearchResults guildId={currentGuildId} />
				</div>
			{/if}
		</div>
	{/if}
	
{/key}

<style>
	#guild-layout {
		display: grid;
		/* flex-direction: row; */
		background-color: var(--panel-channels-bg);
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
		/* padding: 0 4px 10px 4px; */
		margin-right: 5px;
		overflow-y: auto;
		font-weight: 500;
		width: 250px;
	}
	#channels .guild-name {
		padding: 10px 0 10px 14px;
		font-size: 20px;
		font-weight: 600;
		position: sticky;
		top: 0;
		background-color: var(--panel-channels-bg);
		box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.1);
		margin-bottom: 10px;
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

	#backup-helper {
		margin-top: auto;
		padding: 10px 0 10px 14px;
		font-size: 14px;
		font-weight: 600;
		position: sticky;
		bottom: 0;
		background-color: var(--panel-channels-bg);
		box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.1);
	}
</style>
