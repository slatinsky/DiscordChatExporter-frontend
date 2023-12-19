<script lang="ts">
	import type {Sticker } from "src/js/interfaces";
	import ImageGallery from "src/routes/channels/[guildId]/[channelId]/ImageGallery.svelte";
	import MessageStickerLottie from "./MessageStickerLottie.svelte";

	export let stickers: Sticker[];
</script>

<div class="chatlog__reactions">
	{#each stickers as sticker}
		{#if sticker?.format === "Lottie"}
			<MessageStickerLottie asset={sticker.source} />
		{:else}
			<div class="chatlog__sticker">
				<ImageGallery asset={sticker.source} imgclass={"chatlog__sticker-image"} />
			</div>
		{/if}
	{/each}
</div>

<style>
	:global(.chatlog__sticker-image) {
		max-width: 200px;
		height: auto;
	}
</style>