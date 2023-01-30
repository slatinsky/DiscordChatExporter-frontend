<script lang="ts">
	import { checkUrl } from "src/js/helpers";
	import type { Reaction } from "src/js/interfaces";
	import ImageGallery from "src/routes/channels/[guildId]/[channelId]/ImageGallery.svelte";

	export let reactions: Reaction[];
</script>

<div class="chatlog__reactions">
	{#each reactions as reaction}
		<div class="chatlog__reaction" title={reaction.emoji.name}>
			<ImageGallery
				imgclass="chatlog__emoji chatlog__emoji--small"
				alt={reaction.emoji.name}
				asset={reaction.emoji?.image}
				width={reaction.emoji?.image?.width ?? 17}
				height={reaction.emoji?.image?.height ?? 17}
			/> <span class="chatlog__reaction-count">{reaction.count}</span>
		</div>
	{/each}
</div>