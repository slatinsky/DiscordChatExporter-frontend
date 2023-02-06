<script lang="ts">
	import MenuChannel from './MenuChannel.svelte';
	import IconDropdown from '../icons/IconDropdown.svelte';
	import MenuThread from './MenuThread.svelte';
	import { copyTextToClipboard } from 'src/js/helpers';
	import { contextMenuItems } from '../menu/menuStore';

	export let channels: any;
	export let guildId: string;
	export let selectedChannelId: string | null
	// export let onRightClick

	let categoryName = channels[0].category;
	let categoryId = channels[0].categoryId;

	function localStorageIsOpen(categoryId: string) {
		// read json from local storage
		let json = localStorage.getItem('closedCategoryIds') ?? '[]';
		let closedCategoryIds = JSON.parse(json);

		// return true if category is not closed
		return !closedCategoryIds.includes(categoryId);
	}

	function saveToLocalStorage(isOpen: boolean, categoryId: string) {
		// read json from local storage
		let json = localStorage.getItem('closedCategoryIds') ?? '[]';
		let closedCategoryIds = JSON.parse(json);

		// update json
		if (isOpen) {
			closedCategoryIds = closedCategoryIds.filter((id: string) => id != categoryId);
		} else {
			if (!closedCategoryIds.includes(categoryId)) {
				closedCategoryIds.push(categoryId);
			}
		}

		// write json to local storage
		json = JSON.stringify(closedCategoryIds);
		localStorage.setItem('closedCategoryIds', json);
	}

	let isOpen = localStorageIsOpen(categoryId);

	$: saveToLocalStorage(isOpen, categoryId);

	function onRightClick(e, id) {
		$contextMenuItems = [
			{
				"name": "Copy category ID",
				"action": () => {
					copyTextToClipboard(BigInt(id))
				}
			}
		]
	}
</script>

<div class="category" on:click={() => (isOpen = !isOpen)} on:contextmenu|preventDefault={(e) => onRightClick(e, categoryId)}>
	<div class="icon-dropdown {isOpen? '' : 'rotate'}"><IconDropdown size={16}/></div>
	{categoryName}
</div>
{#if isOpen}
	{#each channels as channel}
		<div class="channel">
			<MenuChannel
				name={channel.name}
				id={channel._id}
				{guildId}
				isSelected={selectedChannelId == channel._id}
				threadCount={channel?.threads?.length ?? 0}
			/>
			{#if [channel._id, ...(channel.threads ? channel.threads.map(thread => thread._id) : [])].includes(selectedChannelId)}
				{#if channel.threads}
					{#each channel.threads as thread, i}
						<MenuThread name={thread.name} id={thread._id} {guildId} {selectedChannelId} isLast={i+1 === channel.threads.length}/>
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
