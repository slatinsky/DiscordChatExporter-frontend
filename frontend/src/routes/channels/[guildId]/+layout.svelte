<script>
	import ContextMenu from '../../../components/menu/ContextMenu.svelte';
	import MenuOption from '../../../components/menu/MenuOption.svelte';
	import { isMenuVisible, setMenuVisible } from '../../../components/menu/menuStore';
	import Header from './Header.svelte';
	import SearchResults from './SearchResults.svelte';
	import { searched, found_messages, filters } from './searchStores';
	import { copyTextToClipboard } from '../../../helpers';
	import MenuCategory from './MenuCategory.svelte';
	export let data;
	import { goto } from '$app/navigation';

	// redirect to first channel if no channel in guild is selected
	// if (data.guildId !== undefined && data.channelId === undefined && Object.keys(data.guild.channels).length > 0) {  // data.guildId can be zero (DMs) so we need to check for undefined
    //     goto(`/channels/${data.guildId}/${Object.keys(data.guild.channels)[0]}`);
    // }

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



	let rightClickId = null;
	function onRightClick(e, id) {
		$isMenuVisible = false  // close previous menu
		setTimeout(() => {
			rightClickId = id;
			setMenuVisible(e)
		}, 0);
	}

	$: if (!$isMenuVisible) {
		rightClickId = null
	}
</script>



<div id="guild-layout" class={$searched ? 'with-search' : ''}>
	<div id="channels">
		<div class="guild-name">{data.guildInfo.name}</div>
		{#each Object.values(data.guild.categories) as category}
			<MenuCategory {category} guildId={data.guildId} selectedChannelId={data.channelId} {onRightClick}/>
		{/each}
		{#if data.guildId != '0'}
		<div id="backup-helper">
			<a href="/channels/{data.guildId}/continue">Backup helper</a>
		</div>
		{/if}

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
			{#key $filters}
				<SearchResults guild={data.guild} />
			{/key}
		</div>
	{/if}
</div>

{#if rightClickId}
<ContextMenu let:visible>
	<MenuOption
			on:click={() => copyTextToClipboard(BigInt(rightClickId))}
			text="Copy channel ID" {visible} />
</ContextMenu>
{/if}

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
