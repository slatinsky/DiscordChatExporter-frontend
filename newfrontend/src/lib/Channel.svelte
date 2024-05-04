<script lang="ts">
    import { getGuildState } from "../js/stores/guildState.svelte";
    import { getLayoutState } from "../js/stores/layoutState.svelte";
    import InfiniteScroll from "./InfiniteScroll.svelte";
    import Message from "./message/Message.svelte";

    const guildState = getGuildState()
    const layoutState = getLayoutState()
</script>


{#snippet renderMessageSnippet(message, previousMessage)}
    <Message message={message} previousMessage={previousMessage} />
{/snippet}


<div class="channel-wrapper" class:threadshown={layoutState.threadshown}>
    <div class="channel" >
        <!-- TODO: support change of selectedMessageId without rerender -->
        {#key guildState.channelMessageId}
            <InfiniteScroll ids={guildState.channelMessagesIds} guildId={guildState.guildId} selectedMessageId={guildState.channelMessageId} isThread={false} renderMessageSnippet={renderMessageSnippet} />
        {/key}
    </div>
</div>


<style>
    .channel-wrapper {
        height: 100%;
        overflow: hidden;
    }

    .threadshown {
        border-bottom-right-radius: 8px;
    }
    .channel {
        background-color: #313338;
        height: 100%;
    }
</style>