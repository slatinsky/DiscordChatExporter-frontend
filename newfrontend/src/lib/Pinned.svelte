<script lang="ts">
    import { getGuildState } from "../js/stores/guildState.svelte";
    import { getLayoutState } from "../js/stores/layoutState.svelte";
    import InfiniteScroll from "./InfiniteScroll.svelte";
    import Icon from "./icons/Icon.svelte";
    import Message from "./message/Message.svelte";

    const guildState = getGuildState()
    const layoutState = getLayoutState()
</script>


{#snippet renderMessageSnippet(message, previousMessage)}
    <div class="pinned-message-wrapper">
        <Message message={message} previousMessage={previousMessage} mergeMessages={false} />
    </div>
{/snippet}


{#if guildState.channelPinnedMessagesIds.length === 0}
    <div class="channel-wrapper" class:threadshown={layoutState.threadshown}>
        <div class="pinned-header">
            <div class="header-txt">Pinned Messages</div>
        </div>
        <div class="no-pins-wrapper">
            <Icon name="placeholder/no-pins" width={94} height={120} />
            <div class="no-pins-msg">This channel doesn't have any pinned messages... yet.</div>
        </div>
        <div class="no-pins-footer">
            <div class="footer-title">PROTIP:</div>
            <div class="footer-subtitle">Users with ‘Manage Messages’ permission can pin a message from its context menu.</div>
        </div>
    </div>
{:else}
    <div class="channel-wrapper" class:threadshown={layoutState.threadshown}>
        <div class="pinned-header">
            <div class="header-txt">Pinned Messages</div>
        </div>
        <div class="channel" >
            {#key guildState.channelMessageId}
                <InfiniteScroll ids={guildState.channelPinnedMessagesIds} guildId={guildState.guildId} selectedMessageId={guildState.channelMessageId} isThread={false} showWelcome={false} showSeparators={false} renderMessageSnippet={renderMessageSnippet} />
            {/key}
        </div>
    </div>
{/if}


<style>

    .no-pins-wrapper {
        display: grid;
        place-items: center;
        background-color: #2b2d31;
        color: #b5bac1;
        font-size: 16px;
        padding: 16px;

        .no-pins-msg {
            max-width: 200px;
            margin-top: 20px;
            color: #dbdee1;
            font-size: 16px;
            font-weight: 500;
        }
    }

    .no-pins-footer {
        height: 106px;
        background-color: #1e1f22;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 16px;
        border-bottom-left-radius: 4px;
        border-bottom-right-radius: 4px;

        .footer-title {
            color: #2dc770;
            font-size: 14px;
            font-weight: 700;
        }

        .footer-subtitle {
            font-size: 14px;
            color: #8f9195;
            font-weight: 500;
            text-align: center;
        }
    }

    .channel-wrapper {
        height: calc(100vh - 100px);
        .pinned-header {
            width: 100%;
            height: 52px;
            background-color: #1e1f22;

            display: flex;
            align-items: center;

            border-top-left-radius: 4px;
            border-top-right-radius: 4px;

            .header-txt {
                font-size: 16px;
                font-weight: 500;
                color: #f2f3f5;
                padding: 16px;
            }
        }
    }

    .threadshown {
        border-bottom-right-radius: 8px;
    }
    .channel {
        background-color: #2b2d31;
        height: 100%;

        border-bottom-left-radius: 4px;
        border-bottom-right-radius: 4px;
    }


    .pinned-message-wrapper {
        border: 1px solid #1e1f22;
        border-radius: 4px;
        margin: 3px 8px 3px 8px;
        padding-bottom: 17px;
        background-color: #313338;
    }
</style>