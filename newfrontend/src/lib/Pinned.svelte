<script lang="ts">
    import { getGuildState } from "../js/stores/guildState.svelte";
    import InfiniteScroll from "./InfiniteScroll.svelte";
    import Icon from "./icons/Icon.svelte";
    import Message from "./message/Message.svelte";

    const guildState = getGuildState()

	interface MyProps {
        messageIds: string[];
    }
    let { messageIds }: MyProps = $props();
</script>


{#snippet renderMessageSnippet(index, message, previousMessage)}
    <div class="pinned-message-wrapper" data-messageid={message._id}>
        <Message message={message} previousMessage={previousMessage} showJump={true} mergeMessages={false} />
    </div>
{/snippet}


{#if messageIds.length === 0}
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
            <InfiniteScroll debugname="pinned" ids={messageIds} guildId={guildState.guildId} selectedMessageId={messageIds[0]} renderMessageSnippet={renderMessageSnippet} bottomAligned={false} />
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