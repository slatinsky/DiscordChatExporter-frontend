<script lang="ts">
    import { guilds, selectedGuildId } from "../../js/stores/guildStore";

    $: guild = $guilds.find(g => g._id === $selectedGuildId)
</script>

<div class="guild-name">{guild?.name ?? "Homepage"}</div>

<style>
    .guild-name {
		padding: 13px 0 13px 14px;
		font-weight: 600;
		font-size: 16px;
		/* position: sticky; */
		top: 0;
		background-color: var(--panel-channels-bg);
		box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.1);
		margin-bottom: 10px;
	}
</style>