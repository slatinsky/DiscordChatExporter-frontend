<script lang="ts">
    import { isDateDifferent } from "../js/helpers";
    import { fetchMessageIds } from "../js/stores/api";
    import { getGuildState } from "../js/stores/guildState.svelte";
    import { getLayoutState } from "../js/stores/layoutState.svelte";
    import DateSeparator from "./DateSeparator.svelte";
    import InfiniteScroll3 from "./InfiniteScroll3.svelte";
    import ChannelStart from "./message/ChannelStart.svelte";
    import Message from "./message/Message.svelte";

    const guildState = getGuildState()
    const layoutState = getLayoutState()

    let apiGuildId = $derived(guildState.guildId ? guildState.guildId : "000000000000000000000000")
    let apiChannelId = $derived(guildState.channelId)


    async function fetchMessagesWrapper(direction: "before" | "after" | "around" | "first" | "last", messageId: string | null = null, limit: number) {
        return fetchMessageIds(apiGuildId, apiChannelId, direction, messageId, limit)
    }
</script>

{#snippet channelStartSnippet(message)}
    <ChannelStart channelName={message.channelName} isThread={false} messageAuthor={message.author} />
{/snippet}

{#snippet channelEndSnippet(index, message, previousMessage)}
    <div data-messageid="last">
        this is the end of the channel
    </div>
{/snippet}

{#snippet renderMessageSnippet2(message, previousMessage)}
    <div data-messageid={message._id}>
        {#if message._id === "first"}
            <div>channel start</div>
        {:else if message._id === "last"}
            <div>channel end</div>
        {:else}
            {#if isDateDifferent(previousMessage, message)}
                <DateSeparator messageId={message._id} />
            {/if}
            <Message message={message} previousMessage={previousMessage} />
        {/if}
    </div>
{/snippet}

<div class="channel-wrapper" class:threadshown={layoutState.threadshown}>
    <div class="channel" >
        {#if guildState.channelId !== null}
            <!-- TODO: support change of selectedMessageId without rerender -->
            {#key guildState.channelMessageId}
                {#key apiChannelId}
                <InfiniteScroll3
                    fetchMessages={fetchMessagesWrapper}
                    scrollToMessageId={guildState.channelMessageId}
                    snippetMessage={renderMessageSnippet2}
                    channelStartSnippet={channelStartSnippet}
                />
                {/key}
            {/key}
        {/if}
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