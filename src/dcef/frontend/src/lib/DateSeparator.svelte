<script lang="ts">
    import { timestampFormat } from "../js/stores/settingsStore.svelte";
    import { renderDate, snowflakeToDate } from "../js/time";

    interface MyProps {
        messageId: string;
    }
    let { messageId }: MyProps = $props();
</script>

<div class="date-separator">
    <div class="date-separator-line"></div>
    <div class="date-separator-text">
        {#key $timestampFormat}
            {renderDate(snowflakeToDate(messageId))}
        {/key}
    </div>
    <div class="date-separator-line"></div>
</div>

<style>
    .date-separator {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 10px 15px;
        gap: 5px;

        .date-separator-line {
            width: 100%;
            height: 1px;
            background-color: #3F4147;
        }

        .date-separator-text {
            color: #949BA4;
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
        }
    }
</style>