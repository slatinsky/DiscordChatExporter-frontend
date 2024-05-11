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
<MessageReferenced message={message} referencedMessage={message.referencedMessage} messageState={messageState} />
<div class="avatar-row">
    {#if !messageState.shouldMerge}
        <MessageAvatar author={message.author} on:click={() => viewUserState.setUser(message.author)} messageState={messageState} />
    {:else}
        <div></div>
    {/if}
    <div on:click style="width: 100%;">
        {#if !messageState.shouldMerge}
            <div class="authorline"><MessageAuthorName author={message.author} on:click={() => viewUserState.setUser(message.author)} messageState={messageState} /> <MessageTimestamp channelOrThreadId={message.channelId} timestamp={message.timestamp} messageId={message._id} /></div>
        {/if}
        <div on:contextmenu|preventDefault={e=>onMessageRightClick(e, message)}  style="width: 100%;">
            {#if messageState.isInvite}
                {#if !messageState.messageContentIsLink}
                    <MessageContent message={message} />
                {/if}
                <MessageInvite messageContent={message.content[0].content} />
            {:else}
                {#if !messageState.messageContentIsLink || !message.content[0].content.includes("https://tenor.com/view/")}
                    <div><MessageContent message={message} /></div>
                {/if}
                {#if message.embeds}
                    {#each message.embeds as embed}
                        <div><MessageEmbed embed={embed} messageState={messageState} /></div>
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

    .authorline {
        margin-bottom: 2px;
    }
    .avatar-row {
        display: grid;
        gap: 15px;
        grid-template-columns: 40px 1fr;
        width: 100%;
    }

</style>