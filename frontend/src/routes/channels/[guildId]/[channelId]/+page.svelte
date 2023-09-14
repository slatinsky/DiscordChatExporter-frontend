<script lang="ts">
	import MessageLoader from "../../../../components/messages/MessageLoader.svelte";

	import type { PageServerData } from "../$types";
    export let data: PageServerData

	import Scroller from "src/components/containers/Scroller3.svelte";
	import MesssageSpoilerHandler from "src/components/messages/MesssageSpoilerHandler.svelte";
	import Container from "src/components/containers/Container.svelte";
	import { channelScrollPosition } from "src/components/settings/settingsStore";
	import { onMount } from "svelte";

	$: startPosition = $channelScrollPosition === "bottom" ? data.messages.length - 1 : 0;

	let previousScrollTop = 0;

	// hashchange event listener
	function updateStartPosition() {
		const hash = window.location.hash;
		console.log("hashchange", hash);

		if (hash) {
			// hash is message id
			let index = data.messages.findIndex(m => m._id === hash.slice(1));
			if (index !== -1) {
				startPosition = index;
			}
		}
	}
	$: data.messages, updateStartPosition()

	let jumpToIndex

	$: if (jumpToIndex) {
		jumpToIndex(startPosition)
	}

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
					bind:jumpToIndex
					>
					<div slot="item" let:index>
						{#if data.messages[index]}
						<!-- Added guild name being transfered over to message for some system message like booster. Could be optimized -->
							<MessageLoader messageId={data.messages[index]._id} previousMessageId={data.messages[index - 1]?._id} selectedGuildId={data.guildId} guildName={data.guild.name} />
						{:else}
							<div class="loading">Message didn't load properly</div>
						{/if}
					</div>
				</Scroller>
			<!-- {/key} -->
		</MesssageSpoilerHandler>
	{/if}
{/key}