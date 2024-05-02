<script lang="ts">
    import MenuChannel from "./MenuChannel.svelte";
    import IconDropdown from "../icons/IconDropdown.svelte";
    import { contextMenuItems } from "../../js/stores/menuStore";
    import { copyTextToClipboard } from "../../js/helpers";
    import { getGuildState } from "../../js/stores/guildState.svelte";

	let { category } = $props();

	let isOpen = $state(function() {
        /** returns true if category is not closed */

		let json = localStorage.getItem('closedCategoryIds') ?? '[]';
		let closedCategoryIds = JSON.parse(json);
		return !closedCategoryIds.includes(category._id);
	}())

    function toggle() {
        isOpen = !isOpen
    }

	function saveToLocalStorage(isOpen: boolean, categoryId: string) {
		let json = localStorage.getItem('closedCategoryIds') ?? '[]';
		let closedCategoryIds = JSON.parse(json);
		if (isOpen) {
			closedCategoryIds = closedCategoryIds.filter((id: string) => id != categoryId);
		} else {
			if (!closedCategoryIds.includes(categoryId)) {
				closedCategoryIds.push(categoryId);
			}
		}
		json = JSON.stringify(closedCategoryIds);
		localStorage.setItem('closedCategoryIds', json);
	}

	$effect(() => {
		console.log('categories - saving to local storage', isOpen, category._id)
		saveToLocalStorage(isOpen, category._id);
	})

    function onCategoryRightClick(e, id: string, name: string) {
		$contextMenuItems = [
            {
                "name": isOpen ? "Collapse Category" : "Expand Category",
                "action": () => {
                    isOpen = !isOpen
                }
            },
			{
				"name": "Copy category ID",
				"action": () => {
					copyTextToClipboard(BigInt(id))
				}
			},
			{
				"name": "Copy category name",
				"action": () => {
					copyTextToClipboard(name)
				}
			}
		]
	}

	const guildState = getGuildState()
</script>


<div class="category" on:click={toggle} on:contextmenu|preventDefault={(e) => onCategoryRightClick(e, category._id, category.name)}>
    <div  class="icon-dropdown {isOpen? '' : 'rotate'}"><IconDropdown size={13}/></div>
    <span title="{category.msg_count} messages">{category.name}</span>
</div>
{#each category.channels as channel}
    {#if isOpen || channel._id == guildState.channelId}
        <MenuChannel channel={channel} />
    {/if}
{/each}


<style>
	.category {
		display: flex;
		align-items: center;
		font-size: 12px;
		text-transform: uppercase;
		color: #80848E;;
		cursor: pointer;
        user-select: none;
		letter-spacing: 0.24px;

        margin: 16px 0px 0px 0px;
        font-weight: 600;
	}
    .category:hover {
        color: #DBDEE1;
    }
    .icon-dropdown {
		margin: 2px 2px 0 0;
        transition: transform 0.2s ease-in-out;
    }
	.icon-dropdown.rotate {
		transform: rotate(-90deg);
	}
</style>