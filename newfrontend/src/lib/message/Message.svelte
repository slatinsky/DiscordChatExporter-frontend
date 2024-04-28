<script lang="ts">
    import type { Message } from "../../js/interfaces";
    import AuthorModal from "./AuthorModal.svelte";
    import MessageSystemNotification from "./MessageSystemNotification.svelte";
    import MessageOrdinary from "./MessageOrdinary.svelte";
    import { MessageType } from "./messageEnums";

    export let message: Message

    let authorModal: AuthorModal;

    function isSystemNotification(messageType: string): boolean {
        // https://github.com/Tyrrrz/DiscordChatExporter/blob/81a6d363d1e503787e1aebc5e30b411ef796ef77/DiscordChatExporter.Core/Discord/Data/MessageKind.cs#L20
        const systemNotificationTypes = [
            "RecipientAdd",  // 1
            "RecipientRemove",  // 2
            "Call",  // 3
            "ChannelNameChange",  // 4
            "ChannelIconChange",  // 5
            "ChannelPinnedMessage",  // 6
            "GuildMemberJoin",  // 7
            "ThreadCreated",  // 18
            MessageType.GuildBoost,
            MessageType.GuildBoostTier1,
            MessageType.GuildBoostTier2,
            MessageType.GuildBoostTier3
        ]

        const notSystemNotificationTypes = [
            "Default",  // 0
            "Reply",  // 19
        ]

        return systemNotificationTypes.includes(messageType)
    }
</script>


<div class="message" data-id={message._id}>
    {#if isSystemNotification(message.type)}
        <MessageSystemNotification message={message} authorModal={authorModal} />
    {:else}
        <MessageOrdinary message={message} authorModal={authorModal} />
    {/if}
</div>

{#if message.author}
    <AuthorModal bind:this={authorModal} />
{/if}

<style>
    .message {
        margin-top: 17px;
        padding: 0 20px;
    }
</style>