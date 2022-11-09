<script>
	import IconChannel from '../../../components/icons/IconChannel.svelte';
	import IconChannelWithThreads from '../../../components/icons/IconChannelWithThreads.svelte';
	export let guildId;
	export let id;
	export let name;
	export let isSelected = false;
	export let threadCount = 0;
	export let onRightClick

</script>

<a
	href="/channels/{guildId}/{id}"
	on:contextmenu|preventDefault={(e) => onRightClick(e, id)}
>
	<div class="channel" class:selected={isSelected}>
		{#if threadCount > 0}
			<IconChannelWithThreads />
		{:else}
			<IconChannel />
		{/if}
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
		padding: 4px 8px;
		margin: 1px 8px;
        gap: 5px;
	}

	.channel:hover,
	.channel.selected {
		background-color: var(--channel-bg-hover);
	}

	a {
		color: var(--channel-text-read);
        text-decoration: none;
	}
	.thread-name {
		color: var(--channel-text-read);
	}

	.thread-name.selected {
		color: var(--channel-text-unread) !important;
	}
</style>
