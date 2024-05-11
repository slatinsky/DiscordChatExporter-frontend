<script lang="ts">
    import type { Message } from "../../js/interfaces";
    import MessageSystemNotification from "./MessageSystemNotification.svelte";
    import MessageOrdinary from "./MessageOrdinary.svelte";
    import { MessageType } from "./messageEnums";
    import { snowflakeToDate } from "../../js/time";
    import MessageAutoModerationAction from "./MessageAutoModerationAction.svelte";
    import MesssageSpoilerHandler from "../MesssageSpoilerHandler.svelte";
    import { get } from "svelte/store";

    interface MyProps {
        message: Message;
        previousMessage: Message | null;
    }
    let { message, previousMessage}: MyProps = $props();

    function getMessageState(message: Message, previousMessage: Message | null) {
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

        /**
         * Should this message merge with the previous message?
         */
        function shouldMerge(previousMessage: Message | null, message: Message) {
            // null checks
            if (!previousMessage) {
                console.log("should merge - NO PREVIOUS MESSAGE")
                return false;
            }
            if (!message) {
                return false;
            }

            // if from different author, don't merge
            if (previousMessage.author?._id !== message.author._id) {
                return false;
            }

            // if from different channel, don't merge
            if (previousMessage.channelId !== message.channelId) {
                return false;
            }


            // if more than 5 minutes between messages, don't merge
            let prevDate = snowflakeToDate(previousMessage._id);
            let date = snowflakeToDate(message._id);
            if (date.getTime() - prevDate.getTime() > 7 * 60 * 1000) {
                return false;
            }

            // if is reply, don't merge
            if (message.type === "Reply") {
                return false;
            }

            // without this, join system message may for example be merged with first user message
            if (previousMessage.type !== message.type) {
                return false;
            }

            // if is system notification, don't merge
            if (isSystemNotification(message.type)) {
                return false;
            }

            // if nicknames are different, don't merge
            if (previousMessage.author.nickname !== message.author.nickname) {
                return false;
            }

            return true;
        }

        function messageContentIsLink(messageContent: string): boolean {
            const regex = /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/g
            return regex.test(messageContent)
        }

        function messageContentLinkIsSpoilered(messageContent: string): boolean {
            const regex = /\|\|.*?https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*).*?\|\|/g
            return regex.test(messageContent)
        }

        function messageIsFromDifferentGuild(message: Message): boolean {
            if (!message.reference) {
                return false
            }
            return message.reference.guildId !== message.guildId
        }

        return {
            get isSystemNotification(): boolean {
                return isSystemNotification(message.type)
            },
            get isInvite(): boolean {
                return isInvite(message.content[0].content)
            },
            get shouldMerge(): boolean {
                return shouldMerge(previousMessage, message)
            },
            get messageContentIsLink(): boolean {
                return messageContentIsLink(message.content[0].content)
            },
            get messageContentLinkIsSpoilered(): boolean {
                return messageContentLinkIsSpoilered(message.content[0].content)
            },
            get messageIsFromDifferentGuild(): boolean {
                return messageIsFromDifferentGuild(message)
            }
        }
    }

    const messageState = getMessageState(message, previousMessage)
</script>


<MesssageSpoilerHandler>

    <div class="message" class:notgrouped={!messageState.shouldMerge} data-id={message._id}>
        {#if message.type == "24"}
            <MessageAutoModerationAction message={message} messageState={messageState} />
        {:else if messageState.isSystemNotification}
            <MessageSystemNotification message={message} />
        {:else}
            <MessageOrdinary message={message} messageState={messageState} />
        {/if}
    </div>
</MesssageSpoilerHandler>

<style>
    .message {
        margin-top: 5px;
        padding: 0 20px;
        &.notgrouped {
            margin-top: 17px;
        }
    }
</style>