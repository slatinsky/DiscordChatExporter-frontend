<script lang="ts">
    import { getGuildState, isChannel, isThread } from "../../js/stores/guildState.svelte";
    import { renderTimestamp } from "../../js/time";

    export let timestamp: string;
    export let messageId: string;
    export let channelOrThreadId: string;

    const guildState = getGuildState()

    function changeMessageId(messageId: string) {
        if (isChannel(channelOrThreadId)) {
            guildState.changeChannelMessageId(messageId)
            guildState.pushState()
        }
        else if (isThread(channelOrThreadId)) {
            guildState.changeThreadMessageId(messageId)
            guildState.pushState()
        }
        else {
            console.warn('MessageTimestamp - unknown channel or thread id', channelOrThreadId)
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