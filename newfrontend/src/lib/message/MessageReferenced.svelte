<script lang="ts">
    import { checkUrl } from "../../js/helpers";
    import type { Message } from "../../js/interfaces";
    import { getGuildState } from "../../js/stores/guildState.svelte";
    import { getViewUserState } from "../viewuser/viewUserState.svelte";
    import MessageAuthorName from "./MessageAuthorName.svelte";
    import MessageMarkdown from "./MessageMarkdown.svelte";
    import { onUserRightClick } from "./messageRightClick";
    import Icon from "../icons/Icon.svelte";

    export let message: Message
    export let referencedMessage: Message
    export let messageState;

    const viewUserState = getViewUserState()

    const guildState = getGuildState()

    /*
        NOTE - it is possible to reference another channer or guild (for example reposted annoucements channels)
    */

    async function changeMessageId() {
        if (!message.reference) {
            console.error("No message reference found")
            return
        }

        // save current position
        await guildState.comboSetGuildChannelMessage(message.guildId, message.channelId, message._id)
        await guildState.pushState()

        // set new position
        await guildState.comboSetGuildChannelMessage(message.reference.guildId, message.reference.channelId, message.reference.messageId)
        await guildState.pushState()
    }
</script>

{#if referencedMessage}
    <div class="referenced clickable">
        <div class="referenced-arrow" />
        {#if referencedMessage.author}
            <img class="referenced-avatar" src={checkUrl(referencedMessage.author.avatar)} alt="avatar" on:click on:contextmenu|preventDefault={e=>onUserRightClick(e, referencedMessage.author)}  />
            <MessageAuthorName author={referencedMessage.author} on:click={() => viewUserState.setUser(referencedMessage.author)} />
            <div class="referenced-content" on:click={changeMessageId}>
                {#if referencedMessage.content[0].content !== ""}
                    <MessageMarkdown content={referencedMessage.content[0].content.split("\n")[0]} emotes={referencedMessage?.emotes || []} mentions={referencedMessage?.mentions || []} roles={referencedMessage?.roles || []} channels={referencedMessage?.channels || []} />
                {:else if referencedMessage.attachments && referencedMessage.attachments.length > 0}
                    <i class="click-attachment"><span>Click to see attachment</span><Icon name="reply/attachment" width={20} /></i>
                {/if}
            </div>
        {/if}
    </div>

{:else if messageState.messageIsFromDifferentGuild}
    <div class="referenced">
        <div class="referenced-arrow" />
        <div class="referenced-avatar">
            <Icon name="reply/deleted" width={12} />
        </div>
        <div class="referenced-content clickable" on:click={changeMessageId}>
            <i>This message was created in another server</i>
        </div>
    </div>
<!-- if has reference id, but no reference message was found, the message was probably deleted before it was archived -->
{:else if message.reference && message.reference.messageId}
    <div class="referenced">
        <div class="referenced-arrow" />
        <div class="referenced-avatar">
            <Icon name="reply/deleted" width={12} />
        </div>
        <div class="referenced-content">
            <i>Original message was deleted</i>
        </div>
    </div>
{/if}

<style>
    .referenced {
        display: flex;
        gap: 2px;
        align-items: center;
    }

    .clickable {
        cursor: pointer;
    }

    .referenced-arrow {
        height: 14px;
        margin: 14px 0 4px 16px;
        border-left: 2px solid #4E5058;
        border-top: 2px solid #4E5058;
        border-radius: 8px 0 0 0;
        width: 35px;
    }

    .referenced-avatar {
        width: 16px;
        height: 16px;
        border-radius: 50%;

        /*style background for deleted referenced message*/
        background-color: #1E1F22;
        color: #909399;
        display: grid;
        place-items: center;
    }

    .referenced-content {
        overflow: hidden;
        text-overflow: ellipsis;
        max-height: 33px;

        margin-top: 1px;
        margin-left: 3px;

        color: #b5b6b8;
        font-size: 0.875rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;

        .click-attachment {
            display:flex;
            align-items:center;
            gap: 5px;
        }
    }
</style>