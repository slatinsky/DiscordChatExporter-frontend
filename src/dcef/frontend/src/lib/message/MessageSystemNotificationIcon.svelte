<script lang="ts">
    import { MessageType } from "./messageEnums";
    import Icon from "../icons/Icon.svelte";

    export let messageType: string;
</script>
<div>
    {#if messageType == "RecipientAdd"}
        <Icon name="systemmessage/join" width={16} />
    {:else if messageType == "RecipientRemove"}
        <Icon name="systemmessage/leave" width={16} />
    {:else if messageType == "Call"}
        <Icon name="systemmessage/call" width={16} />
    {:else if messageType == "ChannelNameChange" || messageType == "ChannelIconChange"}
        <Icon name="systemmessage/edit" width={16} />
    {:else if messageType == "ChannelPinnedMessage"}
        <Icon name="systemmessage/pinned" width={16} />
    {:else if messageType == "GuildMemberJoin"}
        <Icon name="systemmessage/join" width={16} />
    {:else if messageType == "ThreadCreated"}
        <Icon name="channeltype/thread" width={16} />
    {:else if messageType == MessageType.GuildBoost || messageType == MessageType.GuildBoostTier1 || messageType == MessageType.GuildBoostTier2 || messageType == MessageType.GuildBoostTier3}
        <Icon name="systemmessage/boost" width={16} />
    {/if}
</div>

<style>
    div {
        color: #949ba4;
    }
</style>