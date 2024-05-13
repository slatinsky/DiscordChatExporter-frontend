<script lang="ts">
    import { getGuildState } from "../../js/stores/guildState.svelte";
    const guildState = getGuildState()
</script>

<div class="guild-name">{guildState.guild?.name ?? "Direct Messages"}</div>

<style>
    .guild-name {
        padding: 13px 0 0 14px;
        height: 47px;
        font-weight: 600;
        font-size: 16px;
        top: 0;
        background-color: var(--panel-channels-bg);
        border-bottom: 1px solid #20222599;
        margin-bottom: 10px;
    }
</style>