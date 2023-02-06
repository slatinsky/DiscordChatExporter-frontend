<script lang="ts">
	import type {Sticker } from "src/js/interfaces";
	import ImageGallery from "src/routes/channels/[guildId]/[channelId]/ImageGallery.svelte";

	export let stickers: Sticker[];
</script>

<div class="chatlog__reactions">
	{#each stickers as sticker}
		<div class="chatlog__sticker">
			<ImageGallery asset={sticker.source} imgclass={"chatlog__sticker-image"} />
		</div>
	{/each}
</div>

<style>
	:global(.chatlog__sticker-image) {
		max-width: 200px;
		max-height: auto;
	}
</style>