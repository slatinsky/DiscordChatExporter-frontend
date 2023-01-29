<!-- Unfinished virtual scroller component -->
<!-- Now renders everything -->

<script lang="ts">
	import type { Message } from "src/js/interfaces";
	import MessageLoader from "src/routes/channels/[guildId]/[channelId]/MessageLoader.svelte";


	export let messages: Message[];
	export let selectedGuildId: string;
</script>

<div class="scroll-area">
	<div class="scroll-content">
		{#each messages as message (message._id)}
			<MessageLoader messageId={message._id} selectedGuildId={selectedGuildId} />
		{/each}
	</div>
</div>


<style>
.scroll-area {
	height: calc(100vh - 51px);
	overflow-y: scroll;
	overflow-x: hidden;
	position: relative;
	width: 100%;
}
</style>