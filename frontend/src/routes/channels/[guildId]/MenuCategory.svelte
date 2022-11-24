<script>
	import MenuChannel from './MenuChannel.svelte';
	import IconDropdown from '../../../components/icons/IconDropdown.svelte';
	import MenuThread from './MenuThread.svelte';

	export let category;
	export let guildId;
	export let selectedChannelId;
	export let onRightClick

	let isOpen = true;
</script>

<div class="category" on:click={() => (isOpen = !isOpen)}>
	<div class="icon-dropdown {isOpen? '' : 'rotate'}"><IconDropdown size={16}/></div>
	{category.name}
</div>
{#if isOpen}
	{#each category.channelIds as channel}
		<div class="channel">
			<MenuChannel
				name={channel.name}
				id={channel.id}
				{guildId}
				isSelected={selectedChannelId == channel.id}
				threadCount={channel?.threads?.length ?? 0}
				{onRightClick}
			/>
			{#if [channel.id, ...(channel.threads ? channel.threads.map(thread => thread.id) : [])].includes(selectedChannelId)}
				{#if channel.threads}
					{#each channel.threads as thread, i}
						<MenuThread name={thread.name} id={thread.id} {guildId} {selectedChannelId} isLast={i+1 === channel.threads.length} {onRightClick} />
					{/each}
				{/if}
			{/if}
		</div>
	{/each}
{/if}

<style>
	.category {
		display: flex;
		align-items: center;
		font-size: 12px;
		text-transform: uppercase;
		color: var(--channel-text-read);
		cursor: pointer;
        user-select: none;

        margin: 16px 0px 0px 0px;
        font-weight: 600;  /*Original 500*/
	}
    .category:hover {
        color: var(--channel-text-read-hover);
    }
    .icon-dropdown {
        transition: transform 0.2s ease-in-out;
    }
	.icon-dropdown.rotate {
		transform: rotate(-90deg);
	}




</style>
