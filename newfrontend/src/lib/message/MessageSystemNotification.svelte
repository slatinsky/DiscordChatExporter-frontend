<script lang="ts">
    import type { Message } from "../../js/interfaces";
    import { changeMessageId, getGuildState } from "../../js/stores/guildState.svelte";
    import { getLayoutState } from "../../js/stores/layoutState.svelte";
    import { getViewUserState } from "../viewuser/viewUserState.svelte";
    import MessageAuthorName from "./MessageAuthorName.svelte";
    import MessageReactions from "./MessageReactions.svelte";
    import MessageSystemNotificationIcon from "./MessageSystemNotificationIcon.svelte";
    import MessageTimestamp from "./MessageTimestamp.svelte";
    import { MessageType } from "./messageEnums";
    import { onMessageRightClick } from "./messageRightClick";

    export let message: Message
    const guildState = getGuildState()
    const layoutState = getLayoutState()

    const viewUserState = getViewUserState()
    $: guildName = guildState.guilds.find(guild => guild._id === message.guildId)?.name ?? "this server"
</script>

<div class="system-message-row">
    <div class="system-message-icon">
        <MessageSystemNotificationIcon messageType={message.type} />
    </div>
    <div class="system-message-content">
        <div>
            <MessageAuthorName author={message.author} on:click={() => viewUserState.setUser(message.author)} />
        </div>

        <span on:contextmenu|preventDefault={e=>onMessageRightClick(e, message)} role="button" tabindex="0">
            {#if message.type == "RecipientAdd"}
                {#if message.mentions}
                    <span class="system-message-text">added <a title={message.mentions[0].name}>{message.mentions[0].nickname}</a> to the group</span>
                {:else}
                    <span class="system-message-text">added someone to the group</span>
                {/if}
            {:else if message.type == "RecipientRemove"}
                {#if message.mentions}
                    {#if message.author._id == message.mentions[0]._id}
                        <span class="system-message-text">left the group</span>
                    {:else}
                        <span class="system-message-text">removed <a title={message.mentions[0].name}>{message.mentions[0].nickname}</a> from the group</span>
                    {/if}
                {:else}
                    <span class="system-message-text">Someone left the group</span>
                {/if}
            {:else if message.type == "Call"}
                <span class="system-message-text">started a call that lasted {Math.floor((Date.parse(message.callEndedTimestamp ?? message.timestamp) - Date.parse(message.timestamp)) / 60000)} minutes</span>
            {:else if message.type == "ChannelNameChange"}
                <span class="system-message-text">{message.content[0].content[0].toLowerCase()}{message.content[0].content.slice(1)}</span>
            {:else if message.type == "ChannelIconChange"}
                <span class="system-message-text">changed the channel icon.</span>
            {:else if message.type == "ChannelPinnedMessage"}
                {#if message?.reference?.messageId}
                    <!-- TODO: this assumes the message was pinned in a channel. But message can be pinned in a thread too  -->
                    <span class="system-message-text">pinned <span class="link" on:click={()=>changeMessageId(message.reference.channelId, message.reference.messageId)}>a message</span> to this channel. See all <span class="link" on:click={layoutState.toggleChannelPinned}>pinned messages</span>.</span>
                {:else}
                    <span class="system-message-text">pinned a message to this channel. See all <span class="link" on:click={layoutState.toggleChannelPinned}>pinned messages</span>.</span>
                {/if}
            {:else if message.type == "ThreadCreated"}
                <span class="system-message-text">started a thread.</span>
            {:else if message.type == "GuildMemberJoin"}
                <span class="system-message-text">joined the server.</span>
                {:else if message.type == MessageType.GuildBoost} <!-- normal boost -->
                <span class="system-message-text">just boosted the server!</span>
                {:else if message.type == MessageType.GuildBoostTier1} <!-- Boost level 1 -->
                <span class="system-message-text">just boosted the server! {guildName} has achieved <strong>Level 1!</strong></span>
                {:else if message.type == MessageType.GuildBoostTier2} <!-- Boost level 2 -->
                <span class="system-message-text">just boosted the server! {guildName} has achieved <strong>Level 2!</strong></span>
                {:else if message.type == MessageType.GuildBoostTier3} <!-- Boost level 3 -->
                <span class="system-message-text">just boosted the server! {guildName} has achieved <strong>Level 3!</strong> </span>
            {:else}
                <span class="system-message-text">{message.content[0].content.toLowerCase()}</span>
            {/if}
            <MessageTimestamp timestamp={message.timestamp} messageId={message._id} channelOrThreadId={message.channelId} />
        </span>
        {#if message.reactions}
            <MessageReactions reactions={message.reactions} />
        {/if}
    </div>
</div>



<style>
    .link {
        color: white;
        font-weight: 500;
        cursor: pointer;
    }
    .link:hover {
        text-decoration: underline;
    }

    .system-message-row {
        display: flex;
        gap: 10px;

        .system-message-icon {
            width: 44px;
            display: grid;
            justify-content: center;
        }

        .system-message-content {
            display: flex;
            gap: 5px;
            .system-message-text {
                color: #949ba4;
            }
        }
    }
</style>