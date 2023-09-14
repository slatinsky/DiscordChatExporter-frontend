<script lang="ts">
	import Header from './Header.svelte';
	import SearchResults from '../../../components/search/SearchResults.svelte';
	import { searchShown, searchResultsMessageIds } from '../../../components/search/searchStores';

	import type { PageServerData } from './$types';
	export let data: PageServerData;

	import ChannelsMenu from '../../../components/channels/MenuCategories.svelte';
	import Container from 'src/components/containers/Container.svelte';
	import { settingsShown } from 'src/components/settings/settingsStore';
	import { isMenuHidden } from 'src/components/menu/menuStore';
	import MenuOpenOverlay from 'src/components/menu/MenuOpenOverlay.svelte';

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
		<div id="guild-layout" class={$searchShown ? 'with-search' : ''} class:hidden={$isMenuHidden}>
			<MenuOpenOverlay />

			<div id="channels">
				<div class="guild-name">{data.guild.name}</div>
				<div id="channelList">
				<ChannelsMenu selectedGuildId={data.guildId} channels={data.channels} selectedChannelId={data.channelId} />
			</div>
				<div class="settings" on:click={()=>$settingsShown = true}>
					<svg aria-hidden="true" role="img" width="20" height="20" viewBox="0 0 24 24"><path fill="currentColor" fill-rule="evenodd" clip-rule="evenodd" d="M19.738 10H22V14H19.739C19.498 14.931 19.1 15.798 18.565 16.564L20 18L18 20L16.565 18.564C15.797 19.099 14.932 19.498 14 19.738V22H10V19.738C9.069 19.498 8.203 19.099 7.436 18.564L6 20L4 18L5.436 16.564C4.901 15.799 4.502 14.932 4.262 14H2V10H4.262C4.502 9.068 4.9 8.202 5.436 7.436L4 6L6 4L7.436 5.436C8.202 4.9 9.068 4.502 10 4.262V2H14V4.261C14.932 4.502 15.797 4.9 16.565 5.435L18 3.999L20 5.999L18.564 7.436C19.099 8.202 19.498 9.069 19.738 10ZM12 16C14.2091 16 16 14.2091 16 12C16 9.79086 14.2091 8 12 8C9.79086 8 8 9.79086 8 12C8 14.2091 9.79086 16 12 16Z"></path></svg>
					Settings
				</div>
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
		height: 100dvh;

		grid-template-areas:
			'channels header header'
			'channels messages messages';

		grid-template-columns: 250px 3fr 2fr;
		grid-template-rows: 50px auto;

		transition: left 0.2s ease-in-out, margin-right 0.2s ease-in-out;
		position: relative;
		left: 0px;
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
		font-weight: 500;
		width: 250px;
	}

	/*Show scrollbar only on hover*/
	#channels {
		overflow-y: auto;
		overflow: overlay; 
		/* Made it so scroll bar don't move the content when hovering channels */
	}
	#channels .guild-name {
		padding: 13px 0 13px 14px;
		font-weight: 600;
		font-size: 16px;
		position: sticky;
		top: 0;
		background-color: var(--panel-channels-bg);
		box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.1);
		margin-bottom: 10px;
	}

	#header {
		grid-area: header;
	}

	#messages {
		grid-area: messages;
		background-color: #313338;
	}

	#search {
		grid-area: search;
	}
	#search:empty {
		display: none;
	}

	:global(#messages .msg-jump) {
		display: none;
	}

	.settings {
		margin-top: auto;
		padding: 10px 0 10px 14px;
		font-size: 14px;
		font-weight: 600;
		position: sticky;
		bottom: 0;
		background-color: #232428;
		box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.1);

		height: 30px;


		display: flex;
		align-items: center;
		gap: 5px;
		/* padding: 10px 10px 10px 0; */
		cursor: pointer;
	}

	.settings:hover {
		background-color: #3d3e45;
	}


	@media (max-width: 1000px) {
		#guild-layout {
			margin-right: -322px;
		}
		#guild-layout.hidden {
			left: -322px;
			margin-right: -322px;
		}

		#guild-layout.with-search {
			grid-template-columns: 250px 3fr 2fr auto-fit;
			grid-template-areas:
				'channels header header header'
				'channels messages messages search';
		}

		#search {
			width: 100vw;
			z-index: 100;
		}
	}
</style>
