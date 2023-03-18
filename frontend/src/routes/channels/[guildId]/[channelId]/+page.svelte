<script lang="ts">
	import MessageLoader from "../../../../components/messages/MessageLoader.svelte";

	import type { PageServerData } from "../$types";
    export let data: PageServerData

	import Scroller from "src/components/containers/Scroller3.svelte";
	import MesssageSpoilerHandler from "src/components/messages/MesssageSpoilerHandler.svelte";
	import Container from "src/components/containers/Container.svelte";
	import { channelScrollPosition } from "src/routes/settingsStore";

	let startPosition = 0;

	function tryToScrollToMessageId(messageId: string) {
		const element = document.querySelector(`#messages [data-message-id='${messageId}']`)
		if (element) {
			const absoluteElement = element.closest(".scroll-absolute-element");
			if (absoluteElement) {
				absoluteElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
			}
		}
	}

	// hashchange event listener
	function updateStartPosition() {
		const hash = window.location.hash;
		console.log("hashchange", hash);

		// try to find message with given ID
		const index = data.messages.findIndex(m => m._id === hash.slice(1));
		if (index !== -1) {
			startPosition = index;
			console.log("hash message found at index", index);

			setTimeout(() => {
				tryToScrollToMessageId(hash.slice(1));
			}, 0);

			setTimeout(() => {
				tryToScrollToMessageId(hash.slice(1));
			}, 300);

			setTimeout(() => {
				tryToScrollToMessageId(hash.slice(1));
			}, 500);
		}
		else {
			console.log("hash message not found");
			startPosition = $channelScrollPosition === "bottom" ? data.messages.length - 1 : 0
		}
	}

	$: data.messages, updateStartPosition()
</script>

<svelte:head>
    <title>{data.channel?.name ?? "Unknown channel"} | DiscordChatExporter frontend</title>
</svelte:head>

<svelte:window on:hashchange={()=>updateStartPosition()}/>

{#key data.channelId}
	{#if data.messages.length === 0}
		<Container>
			{#if data.channelId == 0}
				<div class="txt">Select thread / forum post</div>
			{:else}
				<div class="txt">Channel ID {data.channelId} not found</div>
			{/if}
		</Container>
	{:else}
		<MesssageSpoilerHandler>
			<!-- {#key startPosition} -->
				<Scroller
					itemCount={data.messages.length}
					startPosition={startPosition}
					>
					<div slot="item" let:index>
						<MessageLoader messageId={data.messages[index]._id} previousMessageId={data.messages[index - 1]?._id} selectedGuildId={data.guildId} />
					</div>
				</Scroller>
			<!-- {/key} -->
		</MesssageSpoilerHandler>
	{/if}
{/key}