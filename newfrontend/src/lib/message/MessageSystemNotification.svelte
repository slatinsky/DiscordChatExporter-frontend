<script lang="ts">
    import type { Message } from "../../js/interfaces";
    import { getGuildState } from "../../js/stores/guildState.svelte";
    import { getViewUserState } from "../viewuser/viewUserState.svelte";
    import MessageAuthorName from "./MessageAuthorName.svelte";
    import MessageReactions from "./MessageReactions.svelte";
    import MessageSystemNotificationIcon from "./MessageSystemNotificationIcon.svelte";
    import MessageTimestamp from "./MessageTimestamp.svelte";
    import { MessageType } from "./messageEnums";
    import { onMessageRightClick } from "./messageRightClick";

    export let message: Message
    const guildState = getGuildState()
    const viewUserState = getViewUserState()
    $: guildName = guildState.guilds.find(guild => guild._id === message.guildId)?.name ?? "this server"
</script>

<div class="system-message-row">
    <div class="system-message-icon">
        <MessageSystemNotificationIcon messageType={message.type} />
    </div>
    <div>
        <div>
            <MessageAuthorName author={message.author} on:click={() => viewUserState.setUser(message.author)} />
        </div>

        <span on:contextmenu|preventDefault={e=>onMessageRightClick(e, message)} role="button" tabindex="0">
            {#if message.type == "RecipientAdd"}
                {#if message.mentions}
                    <span>added <a title={message.mentions[0].name}>{message.mentions[0].nickname}</a> to the group</span>
                {:else}
                    <span>added someone to the group</span>
                {/if}
            {:else if message.type == "RecipientRemove"}
                {#if message.mentions}
                    {#if message.author._id == message.mentions[0]._id}
                        <span>left the group</span>
                    {:else}
                        <span>removed <a title={message.mentions[0].name}>{message.mentions[0].nickname}</a> from the group</span>
                    {/if}
                {:else}
                    <span>Someone left the group</span>
                {/if}
            {:else if message.type == "Call"}
                <span>started a call that lasted {Math.floor((Date.parse(message.callEndedTimestamp ?? message.timestamp) - Date.parse(message.timestamp)) / 60000)} minutes</span>
            {:else if message.type == "ChannelNameChange"}
                <span>{message.content[0].content[0].toLowerCase()}{message.content[0].content.slice(1)}</span>
            {:else if message.type == "ChannelIconChange"}
                <span>changed the channel icon.</span>
            {:else if message.type == "ChannelPinnedMessage"}
                {#if message?.reference?.messageId}
                    <span>pinned a message {message.reference.messageId} to this channel.</span>
                {:else}
                    <span>pinned a message to this channel.</span>
                {/if}
            {:else if message.type == "ThreadCreated"}
                <span>started a thread.</span>
            {:else if message.type == "GuildMemberJoin"}
                <span>joined the server.</span>
                {:else if message.type == MessageType.GuildBoost} <!-- Added booster for normal boost -->
                <span>just boosted the server!</span>
                {:else if message.type == MessageType.GuildBoostTier1} <!-- Added booster for Boost level 1 -->
                <span>just boosted the server! {guildName} has achieved <strong>Level 1!</strong></span>
                {:else if message.type == MessageType.GuildBoostTier2} <!-- Added booster for Boost level 2 -->
                <span>just boosted the server! {guildName} has achieved <strong>Level 2!</strong></span>
                {:else if message.type == MessageType.GuildBoostTier3} <!-- Added booster for Boost level 3 -->
                <span>just boosted the server! {guildName} has achieved <strong>Level 3!</strong> </span>
            {:else}
                <!-- TODO More system messages needs to be added in the future here -->
                <span>{message.content[0].content.toLowerCase()}</span>
            {/if}
            <MessageTimestamp timestamp={message.timestamp} />
        </span>
        {#if message.reactions}
            <MessageReactions reactions={message.reactions} />
        {/if}
    </div>
</div>



<style>
    .system-message-row {
        display: flex;
        gap: 10px;
    }

    .system-message-icon {
        width: 44px;
        display: grid;
        justify-content: center;
    }
</style>