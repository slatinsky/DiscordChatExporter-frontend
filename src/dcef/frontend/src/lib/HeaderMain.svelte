<script lang="ts">
    import { getGuildState } from "../js/stores/guildState.svelte";
    import { getLayoutState } from "../js/stores/layoutState.svelte";
    import Pinned from "./Pinned.svelte";
    import Icon from "./icons/Icon.svelte";
    import ChannelIcon from "./menuchannels/ChannelIcon.svelte";
    import SearchInput from "./search/SearchInput.svelte";
    import { getSearchState } from "./search/searchState.svelte";

    const guildState = getGuildState()
    const layoutState = getLayoutState()
    const searchState = getSearchState();



    let showSearchBar = $derived(!searchState.searchManuallyHidden && layoutState.mobile)


    function showSearch() {
        searchState.showSearch()
    }

    function hideSearch() {
        searchState.hideSearch()
    }
</script>


{#if !showSearchBar}
<div class="header-main" class:threadshown={layoutState.threadshown}>
    {#if !(layoutState.searchshown && layoutState.mobile)}
        <div class="channel-name">
            {#if layoutState.mobile}
                <button class="hamburger-icon" onclick={layoutState.toggleSidePanel}>
                    <Icon name="other/hamburger" width={20} />
                </button>
            {/if}
            {#if guildState.channel?.name}
                <ChannelIcon channel={guildState.channel} width={20} />
                <span>{guildState.channel.name}</span>
            {:else}
                <span>Select a channel</span>
            {/if}
        </div>
        <div class="other-wrapper">
            {#if guildState.channelId}
                <div class="pin-wrapper">
                    <div class="pin-btn icon" class:active={layoutState.channelpinnedshown} onclick={layoutState.toggleChannelPinned}>
                        <Icon name="systemmessage/pinned" width={24} />
                    </div>
                    {#if layoutState.channelpinnedshown}
                        <div class="pin-messages">
                            {#key guildState.channelId}
                                <Pinned channelId={guildState.channelId} />
                            {/key}
                        </div>
                    {/if}
                </div>
            {/if}
            {#if layoutState.mobile}
                <button class="icon" onclick={showSearch}>
                    <Icon name="other/magnifying-glass" width={24} />
                </button>
            {:else}
                <div class="search-wrapper">
                    <SearchInput />
                </div>
            {/if}
        </div>
    {:else}
        <SearchInput />
    {/if}
</div>

{/if}
{#if showSearchBar}
    <div class="searchbar">
        <button class="icon icon-back" onclick={hideSearch}>
            <Icon name="systemmessage/leave" width={24} />
        </button>
        <div class="searchinput">
            <SearchInput />
        </div>
    </div>
{/if}



<style>
    .searchbar {
        height: 100%;
        display: flex;
        gap: 8px;
        flex-direction: row;
        align-items: center;
        padding: 0 15px;
        box-sizing: border-box;
        gap: 5px;
        border-bottom: 1px solid #20222599;
        background-color: #313338;

        .icon-back {
            filter: invert(1) grayscale(1);
        }

        .searchinput {
            flex: 1;
        }
    }

    .icon {
        color: #b5bac1;
        cursor: pointer;
        &:hover {
            color: #dbdee1;
        }
        &.active {
            color: white;
        }
    }



    .hamburger-icon {
        cursor: pointer;
        color: #b5bac1;
        margin-right: 10px;
        &:hover {
            color: #dbdee1;
        }
    }

    .search-wrapper {
        position: relative;
    }
    .other-wrapper {
        display: flex;
        gap: 4px;
    }

    .pin-wrapper {
        display: flex;
        position: relative;
        .pin-btn {
            margin: 0 10px;
        }
        .pin-messages {
            position: absolute;
            top: 30px;
            right: 0px;

            width: 400px;
            z-index: 500;
        }
    }


    .header-main {
        height: 100%;
        display: flex;
        flex-direction: row;
        align-items: center;
        padding: 0 15px;
        box-sizing: border-box;
        gap: 5px;
        border-bottom: 1px solid #20222599;
        background-color: #313338;
    }

    .header-main.threadshown {
        border-top-right-radius: 8px;
    }

    .channel-name {
        display: flex;
        gap: 8px;
        font-size: 16px;
        font-weight: 600;
        color: #F2F3F5;
        flex-grow: 3;
    }
</style>