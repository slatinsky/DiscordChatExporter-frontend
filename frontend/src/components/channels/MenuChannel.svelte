<script>
	import IconChannel from 'src/components/icons/IconChannel.svelte';
	import IconChannelWithThreads from 'src/components/icons/IconChannelWithThreads.svelte';
	import IconVoiceChannel from 'src/components/icons/IconVoiceChannel.svelte';
	import IconNewsChannel from 'src/components/icons/IconNewsChannel.svelte';
	import { copyTextToClipboard } from '../../js/helpers';
	import { contextMenuItems, isMenuHidden } from '../menu/menuStore';
	export let guildId;
	export let id;
	export let name;
	export let isSelected = false;
	export let threadCount = 0;
	export let type;

	function onRightClick(e, id) {
		$contextMenuItems = [
			{
				"name": "Copy channel ID",
				"action": () => {
					copyTextToClipboard(BigInt(id))
				}
			},
			{
				"name": "Copy channel name",
				"action": () => {
					copyTextToClipboard(name)
				}
			}
		]
	}
</script>

<a
	href="/channels/{guildId}/{id}"
	on:contextmenu|preventDefault={(e) => onRightClick(e, id)}
>
	<div title="{name}" class="channel" class:selected={isSelected} on:click={()=>$isMenuHidden=true}>
		<div class="channel-icon">
		{#if threadCount > 0}
			<IconChannelWithThreads />
		{:else if type == "GuildVoiceChat"}
		<!-- Would be nice if DiscordChatExporter also export the nsfw boolean so we can have the other types of channel icons. I will Add forum icon eventually -->
			<IconVoiceChannel />
			{:else if type == "GuildNews"}
			<IconNewsChannel/>
			{:else}
			<IconChannel />
		{/if}
	</div>
		<div class="thread-name" class:selected={isSelected}>
			{name}
		</div>
	</div>
</a>

<style>
	.channel {
		display: flex;
		align-items: center;
		border-radius: 4px;
		width: calc(100% - 40x);
		padding: 4px 6px;
		margin: 1px 8px;
        gap: 5px;
	}

	.channel:hover,
	.channel.selected {
		background-color: var(--channel-bg-hover);
		color: #dbdee1;
	}

	a {
		color: var(--channel-text-read);
        text-decoration: none;
	}
	.thread-name {
		color: var(--channel-text-read);
		white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
	width: 200%;
	}

	.channel:hover .thread-name {
		color: #dbdee1;
	}

	.thread-name.selected {
		color: var(--channel-text-unread) !important;
	}

	.channel-icon {
		width: 24px;
		margin-right: 5px;
	}
</style>
