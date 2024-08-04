<script lang="ts">
    import { isDateDifferent } from "../js/helpers";
    import { getGuildState } from "../js/stores/guildState.svelte";
    import { getLayoutState } from "../js/stores/layoutState.svelte";
    import DateSeparator from "./DateSeparator.svelte";
    import InfiniteScroll2 from "./InfiniteScroll2.svelte";
    import ChannelStart from "./message/ChannelStart.svelte";
    import Message from "./message/Message.svelte";

    const guildState = getGuildState()
    const layoutState = getLayoutState()

    let apiGuildId = $derived(guildState.guildId ? guildState.guildId : "000000000000000000000000")
    let apiChannelId = $derived(guildState.channelId)


    export async function fetchMessageIds(direction: "before" | "after" | "around" | "first" | "last", messageId: string | null = null, limit: number) {
        try {
            let response = await fetch(`/api/message-ids-paginated?guild_id=${encodeURIComponent(apiGuildId)}&channel_id=${encodeURIComponent(apiChannelId)}&direction=${direction}&message_id=${encodeURIComponent(messageId)}&limit=${limit}`)
            let messageIds = await response.json()
            return messageIds
        }
        catch (e) {
            console.error("api - Failed to fetch message ids", e)
            return []
        }
    }
</script>


{#snippet renderMessageSnippet(index, message, previousMessage)}
    <!-- {#if index === 0}
        <ChannelStart channelName={message.channelName} isThread={false} messageAuthor={message.author} />
    {/if} -->

    {#if isDateDifferent(previousMessage, message)}
        <DateSeparator messageId={message._id} />
    {/if}

    <div data-messageid={message._id}>
        <Message message={message} previousMessage={previousMessage} />
    </div>
{/snippet}

{#snippet channelStartSnippet(index, message, previousMessage)}
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
            <!-- <ChannelStart channelName={message.channelName} isThread={false} messageAuthor={message.author} /> -->
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
                <!-- <InfiniteScroll
                    debugname="channel"
                    ids={guildState.channelMessagesIds}
                    loadBefore={guildState.loadChannelMessageIdsBefore}
                    loadAfter={guildState.loadChannelMessageIdsAfter}
                    guildId={guildState.guildId}
                    selectedMessageId={guildState.channelMessageId}
                    renderMessageSnippet={renderMessageSnippet}
                    channelStartSnippet={channelStartSnippet}
                    channelEndSnippet={channelEndSnippet}
                    bottomAligned={true}
                /> -->
                {#key apiChannelId}
                <InfiniteScroll2
                    fetchMessageIds={fetchMessageIds}
                    guildId={apiGuildId}
                    snippetMessage={renderMessageSnippet2}
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