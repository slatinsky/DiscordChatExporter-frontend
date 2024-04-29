<script lang="ts">
    import type { Message } from "../../js/interfaces";
    import AuthorModal from "./AuthorModal.svelte";
    import MessageAttachments from "./MessageAttachments.svelte";
    import MessageAuthorName from "./MessageAuthorName.svelte";
    import MessageAvatar from "./MessageAvatar.svelte";
    import MessageContent from "./MessageContent.svelte";
    import MessageEmbed from "./MessageEmbed.svelte";
    import MessageReactions from "./MessageReactions.svelte";
    import MessageReferenced from "./MessageReferenced.svelte";
    import MessageStickers from "./MessageStickers.svelte";
    import MessageTimestamp from "./MessageTimestamp.svelte";
    import { onMessageRightClick } from "./messageRightClick";

    export let message: Message;
    export let authorModal: AuthorModal;

</script>
<MessageReferenced referencedMessage={message.referencedMessage} referenceMessageId={message.reference?.messageId} authorModal={authorModal} />
<div class="avatar-row">
    <MessageAvatar author={message.author} on:click={() => authorModal.viewAuthor(message.author)} />
    <div on:click>
        <div><MessageAuthorName author={message.author} on:click={() => authorModal.viewAuthor(message.author)} /> <MessageTimestamp timestamp={message.timestamp} /></div>
        <div on:contextmenu|preventDefault={e=>onMessageRightClick(e, message)}>
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
    }
</style>