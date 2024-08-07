<script lang="ts">
    import { isDateDifferent } from "../js/helpers";
    import { fetchPinnedMessages } from "../js/stores/api";
    import { getGuildState } from "../js/stores/guildState.svelte";
    import DateSeparator from "./DateSeparator.svelte";
    import InfiniteScroll3 from "./InfiniteScroll3.svelte";
    import Icon from "./icons/Icon.svelte";
    import Message from "./message/Message.svelte";

    const guildState = getGuildState()
    let apiGuildId = $derived(guildState.guildId ? guildState.guildId : "000000000000000000000000")

	interface MyProps {
        channelId: string[];
    }
    let { channelId }: MyProps = $props();

    async function fetchMessagesWrapper(direction: "before" | "after" | "around" | "first" | "last", messageId: string | null = null, limit: number) {
        return fetchPinnedMessages(apiGuildId, channelId, direction, messageId, limit)
    }
</script>


{#snippet renderMessageSnippet(index, message, previousMessage)}
    <div class="pinned-message-wrapper" data-messageid={message._id}>
        <Message message={message} previousMessage={previousMessage} showJump={true} mergeMessages={false} />
    </div>
{/snippet}

{#snippet renderMessageSnippet2(message, previousMessage)}
    <div data-messageid={message._id}>
        {#if message._id === "first"}
            <!-- <ChannelStart channelName={message.channelName} isThread={false} messageAuthor={message.author} /> -->
            <div>pinned start</div>
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

{#if !channelId}
    <div class="channel-wrapper">
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
    <div class="channel-wrapper">
        <div class="pinned-header">
            <div class="header-txt">Pinned Messages</div>
        </div>
        <div class="channel" >
            <!-- <InfiniteScroll
            debugname="pinned"
            ids={messageIds}
            guildId={guildState.guildId}
            selectedMessageId={messageIds[0]}
            renderMessageSnippet={renderMessageSnippet}
            bottomAligned={false} /> -->
            <InfiniteScroll3
                fetchMessages={fetchMessagesWrapper}
                guildId={apiGuildId}
                scrollToMessageId={"last"}
                snippetMessage={renderMessageSnippet2}
            />
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
        /* max-height: calc(100vh - 120px); */
        /* height: min-content; */
        /* height: calc(100vh - 120px);
         */
         border: 1px solid #25262a;
         border-radius: 4px;
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
        .channel {
            background-color: #2b2d31;
            height: calc(100vh - 120px);

            border-bottom-left-radius: 4px;
            border-bottom-right-radius: 4px;
        }
    }


    .pinned-message-wrapper {
        border: 1px solid #1e1f22;
        border-radius: 4px;
        margin: 3px 8px 3px 8px;
        padding-bottom: 17px;
        background-color: #313338;
    }
</style>