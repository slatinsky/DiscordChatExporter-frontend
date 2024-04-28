<script lang="ts">
    import ChannelPinnedMessage from "../icons/ChannelPinnedMessage.svelte";
    import IconCall from "../icons/IconCall.svelte";
    import IconChannelIconNameChange from "../icons/IconChannelIconNameChange.svelte";
    import IconGuildBoosted from "../icons/IconGuildBoosted.svelte";


    import IconGuildJoin from "../icons/IconGuildJoin.svelte";
    import IconGuildLeave from "../icons/IconGuildLeave.svelte";
    import IconThreadCreated from "../icons/IconThreadCreated.svelte";
    import { MessageType } from "./messageEnums";

    export let messageType: string;
</script>
<div>
    {#if messageType == "RecipientAdd"}
        <IconGuildJoin />
    {:else if messageType == "RecipientRemove"}
        <IconGuildLeave />
    {:else if messageType == "Call"}
        <IconCall />
    {:else if messageType == "ChannelNameChange" || messageType == "ChannelIconChange"}
        <IconChannelIconNameChange />
    {:else if messageType == "ChannelPinnedMessage"}
        <ChannelPinnedMessage />
    {:else if messageType == "GuildMemberJoin"}
        <IconGuildJoin />
    {:else if messageType == "ThreadCreated"}
        <IconThreadCreated />
    {:else if messageType == MessageType.GuildBoost || messageType == MessageType.GuildBoostTier1 || messageType == MessageType.GuildBoostTier2 || messageType == MessageType.GuildBoostTier3}
        <IconGuildBoosted />
    {/if}
</div>