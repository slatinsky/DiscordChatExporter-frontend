<script lang="ts">
    import { selectedChannelId } from "../../js/stores/guildStore";
    import MenuChannel from "./MenuChannel.svelte";
    import IconDropdown from "../icons/IconDropdown.svelte";

    export let category
    let isOpen = true

    function toggle() {
        isOpen = !isOpen
    }
</script>


<div class="category" on:click={toggle}>
    <div  class="icon-dropdown {isOpen? '' : 'rotate'}"><IconDropdown size={13}/></div>
    {category.name}
</div>
{#each category.channels as channel}
    {#if isOpen || channel._id == $selectedChannelId}
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