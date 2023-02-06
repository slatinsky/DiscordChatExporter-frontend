<script lang="ts">
	import MessageLoader from "../../../../components/messages/MessageLoader.svelte";

	import type { PageServerData } from "../$types";
    export let data: PageServerData

	import Scroller from "src/components/containers/Scroller3.svelte";
	import MesssageSpoilerHandler from "src/components/messages/MesssageSpoilerHandler.svelte";
	import Container from "src/components/containers/Container.svelte";
	import { channelScrollPosition } from "src/routes/settingsStore";
</script>

<svelte:head>
    <title>{data.channel?.name ?? "Unknown channel"} | DiscordChatExporter frontend</title>
</svelte:head>



{#key data.channelId}
	{#if data.messages.length === 0}
		<Container>
			<div class="txt">Channel ID {data.channelId} not found</div>
		</Container>
	{:else}
		<MesssageSpoilerHandler>
			<Scroller
				itemCount={data.messages.length}
				startPosition={$channelScrollPosition === "bottom" ? data.messages.length - 1 : 0}
				>
				<div slot="item" let:index>
					<MessageLoader messageId={data.messages[index]._id} previousMessageId={data.messages[index - 1]?._id} selectedGuildId={data.guildId} />
				</div>
			</Scroller>
		</MesssageSpoilerHandler>
	{/if}
{/key}


<style>
	.txt {
		font-size: 32px;
		padding-top: 20px;
		padding-left: 20px;
	}
</style>