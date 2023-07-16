<script lang="ts">
	import MessageLoader from "../../../../components/messages/MessageLoader.svelte";

	import type { PageServerData } from "../$types";
    export let data: PageServerData

	import Scroller from "src/components/containers/Scroller3.svelte";
	import MesssageSpoilerHandler from "src/components/messages/MesssageSpoilerHandler.svelte";
	import Container from "src/components/containers/Container.svelte";
	import { channelScrollPosition } from "src/components/settings/settingsStore";
	import { onMount } from "svelte";

	let startPosition = 0;

	let previousScrollTop = 0;
	function tryToScrollToMessageId(messageId: string) {
		console.log("tryToScrollToMessageId", messageId);
		const element = document.querySelector(`#messages [data-message-id='${messageId}']`)
		if (element) {
			const absoluteElement = element.closest(".scroll-absolute-element");
			if (absoluteElement) {
				const currentScrollTop = element.offsetTop;  // scroll only if element position was updated
				if (currentScrollTop !== previousScrollTop || currentScrollTop === 0) {
					console.log("scrolling to message", currentScrollTop, previousScrollTop);
					absoluteElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
				}
			}

			previousScrollTop = element.offsetTop;
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

			let timeouts = [0, 300, 500, 1000, 1500, 2000];
			// use for loop
			for (let i = 0; i < timeouts.length; i++) {
				setTimeout(() => {
					tryToScrollToMessageId(hash.slice(1));
				}, timeouts[i]);
			}
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