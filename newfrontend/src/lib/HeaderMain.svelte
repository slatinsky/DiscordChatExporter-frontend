<script lang="ts">
    import { getGuildState } from "../js/stores/guildState.svelte";
    import { getLayoutState } from "../js/stores/layoutState.svelte";
    import Pinned from "./Pinned.svelte";
    import Icon from "./icons/Icon.svelte";

    const guildState = getGuildState()
    const layoutState = getLayoutState()
</script>


<div class="header-main" class:threadshown={layoutState.threadshown}>
    <div class="channel-icon">
        <Icon name="channeltype/channel" width={20} />
    </div>
    <div class="channel-name">{guildState.channel?.name ?? "Select a channel"}</div>
    <div style="display: flex;">
        {#if guildState.channelId}
            <div class="pin-wrapper">
                <div class="pin-btn" class:active={layoutState.channelpinnedshown} onclick={layoutState.toggleChannelPinned}>
                    <Icon name="systemmessage/pinned" width={24} />
                </div>
                {#if layoutState.channelpinnedshown}
                    <div class="pin-messages">
                        {#key guildState.channelMessageId}
                            <Pinned messageIds={guildState.channelPinnedMessagesIds} />
                        {/key}
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>



<style>
    .channel-icon {
        display: grid;
        place-items: center;
    }

    .pin-wrapper {
        position: relative;
        .pin-btn {
            cursor: pointer;
            color: #b5bac1;
            &:hover {
                color: #dbdee1;
            }
            &.active {
                color: white;
            }
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
        font-size: 16px;
        font-weight: 600;
        color: #F2F3F5;
        flex-grow: 3;
    }
</style>