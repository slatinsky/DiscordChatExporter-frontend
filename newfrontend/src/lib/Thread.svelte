<script lang="ts">
    import { getGuildState } from "../js/stores/guildState.svelte";
    import InfiniteScroll from "./InfiniteScroll.svelte";
    import IconX from "./icons/IconX.svelte";
    import Message from "./message/Message.svelte";

    function destroyThreadView() {
        guildState.changeThreadId(null)
    }

    const guildState = getGuildState()
</script>


<div class="thread-wrapper">
    <div class="header-main">
        <div class="thread-name">{guildState.thread?.name ?? "Select a thread"}</div>
        <div on:click={destroyThreadView} style="cursor:pointer; display: grid; place-items: center;">
            <IconX />
        </div>
    </div>
    <div class="thread">
        <!-- TODO: support change of threadMessageId without rerender -->
        {#key guildState.threadMessageId}
            <InfiniteScroll ids={guildState.threadMessagesIds} guildId={guildState.guildId} selectedMessageId={guildState.threadMessageId} isThread={true}>
                <div slot="item" let:message let:previousMessage>
                    <Message message={message} previousMessage={previousMessage} />
                </div>
            </InfiniteScroll>
        {/key}
    </div>
</div>


<style>
    .thread-wrapper {
        height: 100%;
        margin-left: 7px;
        background-color: #313338;
        display: flex;
        flex-direction: column;

        border-top-left-radius: 8px;
        border-bottom-left-radius: 8px;
        overflow: hidden;
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