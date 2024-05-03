<script lang="ts">
    import type { Message } from "../../js/interfaces";
    import MessageSystemNotification from "./MessageSystemNotification.svelte";
    import MessageOrdinary from "./MessageOrdinary.svelte";
    import { MessageType } from "./messageEnums";

    interface MyProps {
        message: Message;
    }
    let { message}: MyProps = $props();

    function getMessageState(message: Message) {
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

        function isInvite(messageContent: string): boolean {
            const inviteRegex = /(https?:\/\/)?(www\.)?((discordapp\.com\/invite)|(discord\.gg))\/(\w+)/
            return inviteRegex.test(messageContent)
        }

        return {
            get isSystemNotification(): boolean {
                return isSystemNotification(message.type)
            },
            get isInvite(): boolean {
                return isInvite(message.content[0].content)
            },
        }
    }

    const messageState = getMessageState(message)
</script>


<div class="message" data-id={message._id}>
    {#if messageState.isSystemNotification}
        <MessageSystemNotification message={message} />
    {:else}
        <MessageOrdinary message={message} messageState={messageState} />
    {/if}
</div>

<style>
    .message {
        margin-top: 17px;
        padding: 0 20px;
    }
</style>