<script lang="ts">
    import MenuCategory from "./MenuCategory.svelte";
    import MenuGuildName from "./MenuGuildName.svelte";
    import AccountSwitcher from "../accountswitcher/AccountSwitcher.svelte";
    import { getGuildState } from "../../js/stores/guildState.svelte";

    const guildState = getGuildState()
</script>

<div class="categories-col">
    <MenuGuildName />
    <div class="categories-wrapper">
        {#if guildState.categories.length === 0}
            <div class="error">No channels found</div>
        {/if}
        {#each guildState.categories as category}
            <MenuCategory category={category} />
        {/each}
    </div>
    <AccountSwitcher />
</div>


<style>
    .categories-col {
        display: flex;
        flex-direction: column;
        height: 100%;
        border-top-left-radius: 8px;
        background-color: #2B2D31;
        overflow: hidden;
    }
    .error {
        padding: 10px 15px;
        color: #80848E;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.24px;
        font-weight: 600;
    }
    .categories-wrapper {
        overflow-y: scroll;
        height: 100%;
        box-sizing: border-box;
        margin-right: 11px;
    }

    .categories-wrapper {
        margin-right: 0;
    }

    .categories-wrapper::-webkit-scrollbar-track {
        background-color: #2b2d31;
    }
    .categories-wrapper::-webkit-scrollbar-corner {
        background-color: #646464;
    }
    .categories-wrapper::-webkit-resizer {
        background-color: #666;
    }
    .categories-wrapper::-webkit-scrollbar {
        width: 0px;
        height: 3px;
    }
    .categories-wrapper:hover::-webkit-scrollbar {
        width: 11px;
    }
    .categories-wrapper::-webkit-scrollbar-thumb {
        height: 50px;
        background-color: #1a1b1e;
        border-radius: 3px;

        width: 5px;
        border-radius: 10px;

        /*left+right scrollbar padding magix*/
        background-clip: padding-box;
        border: 3px solid rgba(0, 0, 0, 0);
    }
</style>

