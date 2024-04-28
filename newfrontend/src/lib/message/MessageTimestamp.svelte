<script lang="ts">
    import { renderTimestamp } from "../../js/time";

    export let timestamp: string;
</script>

<span class="timestamp">{renderTimestamp(timestamp)}</span>

<style>
    .timestamp {
        color: #a3a6aa;
        font-size: 0.75rem;
        font-weight: 500;
    }
</style>