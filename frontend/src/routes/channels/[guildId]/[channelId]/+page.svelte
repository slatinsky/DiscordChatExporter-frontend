<script lang="ts">
	import MessageLoader from "../../../../components/messages/MessageLoader.svelte";

	import type { PageServerData } from "../$types";
    export let data: PageServerData

	import Scroller from "src/components/Scroller2.svelte";
	import MesssageSpoilerHandler from "src/components/messages/MesssageSpoilerHandler.svelte";
</script>

<svelte:head>
    <title>{data.channel?.name ?? "Unknown channel"} | DiscordChatExporter frontend</title>
</svelte:head>



{#key data.channelId}

<MesssageSpoilerHandler>
	<Scroller
		itemCount={data.messages.length}
		>
		<div slot="item" let:index>
			<MessageLoader messageId={data.messages[index]._id} previousMessageId={data.messages[index - 1]?._id} selectedGuildId={data.guildId} />
		</div>
	</Scroller>
</MesssageSpoilerHandler>

{/key}


