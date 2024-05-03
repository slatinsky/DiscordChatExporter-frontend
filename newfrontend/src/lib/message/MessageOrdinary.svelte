<script lang="ts">
    import type { Message } from "../../js/interfaces";
    import { getViewUserState } from "../viewuser/viewUserState.svelte";
    import MessageAttachments from "./MessageAttachments.svelte";
    import MessageAuthorName from "./MessageAuthorName.svelte";
    import MessageAvatar from "./MessageAvatar.svelte";
    import MessageContent from "./MessageContent.svelte";
    import MessageEmbed from "./MessageEmbed.svelte";
    import MessageInvite from "./MessageInvite.svelte";
    import MessageReactions from "./MessageReactions.svelte";
    import MessageReferenced from "./MessageReferenced.svelte";
    import MessageStickers from "./MessageStickers.svelte";
    import MessageTimestamp from "./MessageTimestamp.svelte";
    import { onMessageRightClick } from "./messageRightClick";

    export let message: Message;
    export let messageState;
    const viewUserState = getViewUserState()

</script>
<MessageReferenced message={message} referencedMessage={message.referencedMessage} referenceMessageId={message.reference?.messageId} />
<div class="avatar-row">
    <MessageAvatar author={message.author} on:click={() => viewUserState.setUser(message.author)} />
    <div on:click style="width: 100%;">
        <div><MessageAuthorName author={message.author} on:click={() => viewUserState.setUser(message.author)} /> <MessageTimestamp channelOrThreadId={message.channelId} timestamp={message.timestamp} messageId={message._id} /></div>
        <div on:contextmenu|preventDefault={e=>onMessageRightClick(e, message)}  style="width: 100%;">
            {#if messageState.isInvite}
                <MessageInvite messageContent={message.content[0].content} />
            {:else}
                <div><MessageContent message={message} /></div>
                {#if message.embeds}
                    {#each message.embeds as embed}
                        <div><MessageEmbed embed={embed} /></div>
                    {/each}
                {/if}
                {#if message.attachments}
                    <div><MessageAttachments attachments={message.attachments} /></div>
                {/if}
                {#if message.stickers}
                    <MessageStickers stickers={message.stickers} />
                {/if}
            {/if}
        </div>
        {#if message.reactions}
            <MessageReactions reactions={message.reactions} />
        {/if}
    </div>
</div>

<style>
    .avatar-row {
        display: flex;
        gap: 15px;
        width: 100%;
    }
</style>