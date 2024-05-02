<script lang="ts">
    import { getGuildState, isChannel } from "../../js/stores/guildState.svelte";
    import { renderTimestamp } from "../../js/time";

    export let timestamp: string;
    export let messageId: string;
    export let channelOrThreadId: string;

    const guildState = getGuildState()

    function changeMessageId(messageId: string) {
        if (isChannel(channelOrThreadId)) {
            guildState.changeChannelMessageId(messageId)
        } else {
            guildState.changeThreadMessageId(messageId)
        }
    }
</script>

<span class="timestamp" on:click={()=>changeMessageId(messageId)}>{renderTimestamp(timestamp)}</span>

<style>
    .timestamp {
        color: #a3a6aa;
        font-size: 0.75rem;
        font-weight: 500;
        cursor: pointer;
    }
</style>