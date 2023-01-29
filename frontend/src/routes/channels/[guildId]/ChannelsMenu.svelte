<script lang="ts">
	import type { Channel } from "src/js/interfaces";


	export let channels: Channel[] = [];
	export let selectedChannelId: string | null = null;
	export let selectedGuildId: string | null = null;
</script>


<!-- {#each Object.values(data.guild.categories) as category}
	<MenuCategory {category} guildId={data.guildId} selectedChannelId={data.channelId} {onRightClick}/>
{/each} -->

{#each Object.values(channels) as channel}
	<a href="/channels/{selectedGuildId}/{channel._id}">{channel.name}</a>
{/each}