<script lang="ts">
    import { isDateDifferent } from "../js/helpers";
    import { fetchMessageIds } from "../js/stores/api";
    import { getGuildState } from "../js/stores/guildState.svelte";
    import { getLayoutState } from "../js/stores/layoutState.svelte";
    import DateSeparator from "./DateSeparator.svelte";
    import InfiniteScroll3 from "./InfiniteScroll3.svelte";
    import Pinned from "./Pinned.svelte";
    import Icon from "./icons/Icon.svelte";
    import ChannelIcon from "./menuchannels/ChannelIcon.svelte";
    import ChannelStart from "./message/ChannelStart.svelte";
    import Message from "./message/Message.svelte";

    function destroyThreadView() {
        guildState.changeThreadId(null)
        guildState.pushState()
    }

    const guildState = getGuildState()
    const layoutState = getLayoutState()

    let apiGuildId = $derived(guildState.guildId ? guildState.guildId : "000000000000000000000000")
    let apiChannelId = $derived(guildState.threadId)

    export async function fetchMessagesWrapper(direction: "before" | "after" | "around" | "first" | "last", messageId: string | null = null, limit: number) {
        if (apiChannelId === null) {
            return []
        }
        return fetchMessageIds(apiGuildId, apiChannelId, direction, messageId, limit)
    }
</script>

{#snippet channelStartSnippet(message)}
    <ChannelStart channelName={message.channelName} isThread={true} messageAuthor={message.author} />
{/snippet}

{#snippet renderMessageSnippet2(message, previousMessage)}
    <div data-messageid={message._id}>
        {#if message._id === "first"}
            <div>thread start</div>
        {:else if message._id === "last"}
            <div>thread end</div>
        {:else}
            {#if isDateDifferent(previousMessage, message)}
                <DateSeparator messageId={message._id} />
            {/if}
            <Message message={message} previousMessage={previousMessage} />
        {/if}
    </div>
{/snippet}


<div class="thread-wrapper">
    <div class="header-main">
        <div class="thread-name">
            {#if layoutState.mobile}
                <div class="hamburger-icon" onclick={layoutState.toggleSidePanel}>
                    <Icon name="other/hamburger" width={20} />
                </div>
            {/if}
            {#if guildState.thread?.name}
                <ChannelIcon channel={guildState.thread} width={20} /><span>{guildState.thread.name}</span>
            {:else}
                <span>Select a thread</span>
            {/if}
        </div>
        <div class="pin-wrapper">
            <div class="pin-btn" class:active={layoutState.threadpinnedshown} onclick={layoutState.toggleThreadPinned}>
                <Icon name="systemmessage/pinned" width={24} />
            </div>
            {#if layoutState.threadpinnedshown}
                <div class="pin-messages">
                    {#key guildState.threadMessageId}
                        <Pinned channelId={guildState.threadId} />
                    {/key}
                </div>
            {/if}
        </div>
        <div onclick={destroyThreadView} style="cursor:pointer; display: grid; place-items: center;">
            <Icon name="modal/x" width={24} />
        </div>
    </div>
    <div class="thread">
        <!-- TODO: support change of threadMessageId without rerender -->
        {#key guildState.threadId}
            {#key guildState.threadMessageId}
                <InfiniteScroll3
                    fetchMessages={fetchMessagesWrapper}
                    scrollToMessageId={guildState.threadMessageId}
                    snippetMessage={renderMessageSnippet2}
                    channelStartSnippet={channelStartSnippet}
                />
            {/key}
        {/key}
    </div>
</div>


<style>
    .hamburger-icon {
        cursor: pointer;
        color: #b5bac1;
        margin-right: 10px;
        &:hover {
            color: #dbdee1;
        }
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

    .thread-wrapper {
        height: 100%;
        margin-left: 7px;
        background-color: #313338;
        display: flex;
        flex-direction: column;

        border-top-left-radius: 8px;
        border-bottom-left-radius: 8px;
        overflow: hidden;

        z-index: 101;
    }
    .header-main {
        height: 47px;
        display: flex;
        flex-direction: row;
        align-items: center;
        padding: 5px 10px 5px 15px;
        box-sizing: border-box;
        gap: 5px;
        border-bottom: 1px solid #20222599;
    }

    .thread-name {
        display: flex;
        gap: 8px;
        font-size: 16px;
        font-weight: 600;
        color: #F2F3F5;
        flex-grow: 3;
    }

    .thread {
        overflow-y: auto;
        height: 100%;
    }

    .thread::-webkit-scrollbar-track {
        background-color: #2b2d31;
    }
    .thread::-webkit-scrollbar-corner {
        background-color: #646464;
    }

    .thread::-webkit-resizer {
        background-color: #666;
    }
    .thread::-webkit-scrollbar-track-piece {
        background-color:#313338;
    }
    .thread::-webkit-scrollbar {
        height: 3px;
        width: 14px;
    }
    .thread::-webkit-scrollbar-thumb {
        height: 50px;
        background-color: #1a1b1e;

        width: 5px;
        border-radius: 10px;

        /*left+right scrollbar padding magix*/
        background-clip: padding-box;
        border: 3px solid rgba(0, 0, 0, 0);
    }
</style>