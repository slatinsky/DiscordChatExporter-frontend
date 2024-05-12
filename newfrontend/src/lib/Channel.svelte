<script lang="ts">
    import { isDateDifferent } from "../js/helpers";
    import { getGuildState } from "../js/stores/guildState.svelte";
    import { getLayoutState } from "../js/stores/layoutState.svelte";
    import DateSeparator from "./DateSeparator.svelte";
    import InfiniteScroll from "./InfiniteScroll.svelte";
    import ChannelStart from "./message/ChannelStart.svelte";
    import Message from "./message/Message.svelte";

    const guildState = getGuildState()
    const layoutState = getLayoutState()
</script>


{#snippet renderMessageSnippet(index, message, previousMessage)}
    {#if index === 0}
        <ChannelStart channelName={message.channelName} isThread={false} messageAuthor={message.author} />
    {/if}

    {#if isDateDifferent(previousMessage, message)}
        <DateSeparator messageId={message._id} />
    {/if}

    <div data-messageid={message._id}>
        <Message message={message} previousMessage={previousMessage} />
    </div>
{/snippet}


<div class="channel-wrapper" class:threadshown={layoutState.threadshown}>
    <div class="channel" >
        <!-- TODO: support change of selectedMessageId without rerender -->
        {#key guildState.channelMessageId}
            <InfiniteScroll ids={guildState.channelMessagesIds} guildId={guildState.guildId} selectedMessageId={guildState.channelMessageId} renderMessageSnippet={renderMessageSnippet} bottomaligned={true} />
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