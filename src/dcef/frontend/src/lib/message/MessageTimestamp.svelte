<script lang="ts">
    import { changeMessageId } from "../../js/stores/guildState.svelte";
    import { renderTimestamp } from "../../js/time";

    export let timestamp: string;
    export let messageId: string;
    export let channelOrThreadId: string;


</script>

<span class="timestamp" on:click={()=>changeMessageId(channelOrThreadId, messageId)}>{renderTimestamp(timestamp)}</span>

<style>
    .timestamp {
        color: #a3a6aa;
        font-size: 0.75rem;
        font-weight: 500;
        cursor: pointer;
    }
</style>