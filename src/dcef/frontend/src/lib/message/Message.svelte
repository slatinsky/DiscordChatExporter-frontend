<script lang="ts">
    import type { Message } from "../../js/interfaces";
    import MessageSystemNotification from "./MessageSystemNotification.svelte";
    import MessageOrdinary from "./MessageOrdinary.svelte";
    import { MessageType } from "./messageEnums";
    import { snowflakeToDate } from "../../js/time";
    import MessageAutoModerationAction from "./MessageAutoModerationAction.svelte";
    import MesssageSpoilerHandler from "../MesssageSpoilerHandler.svelte";
    import { getGuildState } from "../../js/stores/guildState.svelte";
    import { getLayoutState } from "../../js/stores/layoutState.svelte";
    import { getSearchState } from "../search/searchState.svelte";

    interface MyProps {
        message: Message;
        previousMessage: Message | null;
        mergeMessages?: boolean;
        showJump?: boolean;
    }
    let { message, previousMessage, mergeMessages=true, showJump=false}: MyProps = $props();

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

        function inviteIds(messageContent: string): string[] {
            const inviteRegex = /(https?:\/\/)?(www\.)?((discordapp\.com\/invite)|(discord\.gg))\/(\w+)/
            let ids = []
            let match = messageContent.match(inviteRegex)
            while (match) {
                ids.push(match[6])
                messageContent = messageContent.replace(match[0], "")
                match = messageContent.match(inviteRegex)
            }
            return ids
        }

        /**
         * Should this message merge with the previous message?
         */
        function shouldMerge(previousMessage: Message | null, message: Message) {
            if (!mergeMessages) {
                return false;
            }
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
            if (message.reference.guildId === null) {
                // bug in older exports where guildId is null in referenced messages, but message.reference.channelId and message.reference.messageId is set correctly
                // assume it's from the same guild, so return false
                return false
            }
            return message.reference.guildId !== message.guildId
        }

        return {
            get isSystemNotification(): boolean {
                return isSystemNotification(message.type)
            },
            get inviteIds(): string[] {
                return inviteIds(message.content[0].content)
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

    const guildState = getGuildState()
    const layoutState = getLayoutState()
    const searchState = getSearchState();


    async function jumpToMessage(){
        await guildState.comboSetGuildChannelMessage(message.guildId, message.channelId, message._id)
        await guildState.pushState()
        if (layoutState.mobile) {
            searchState.hideSearch()
        }
    }

    const messageState = getMessageState(message, previousMessage)
</script>


<MesssageSpoilerHandler>

    <div class="message" class:jumpable={showJump} class:notgrouped={!messageState.shouldMerge} data-id={message._id} class:ismobile={layoutState.mobile}>
        <button class="jump-btn" on:click={jumpToMessage}>Jump</button>
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
        position: relative;

        &.notgrouped {
            margin-top: 17px;
        }

        .jump-btn {
            display: none;
        }
    }

    .message.jumpable {
        .jump-btn {
            cursor: pointer;
            display: none;
            position: absolute;
            top: -10px;
            right: 5px;
            padding: 4px;

            background-color: #1e1f22;
            color: #b5bac1;
            font-size: 12px;
            font-weight: 500;
            border-radius: 3px;
        }
        &:hover .jump-btn {
            display: block;
        }
    }

    .message.jumpable.ismobile .jump-btn {
        display: block;
    }
</style>