<script lang="ts">
	import { currentUserId } from "../settings/settingsStore";
	import { checkUrl } from "src/js/helpers";
	import type { Reaction } from "src/js/interfaces";
	import ReactionsModal from "src/routes/channels/[guildId]/[channelId]/ReactionsModal.svelte";

	export let reactions: Reaction[];

	let reactionsModal: ReactionsModal;
</script>

<ReactionsModal {reactions} bind:this={reactionsModal} />

<div class="chatlog__reactions">
	{#each reactions as reaction}
		{@const emojiUsers = reaction?.users?.map(user => user._id) ?? []}
		<div class:me={emojiUsers.includes($currentUserId)} class="chatlog__reaction" title=":{reaction.emoji.name}:" on:click={reactionsModal.viewReactions(reaction)}>
			<img
				class='chatlog__emoji chatlog__emoji--small'
				src={checkUrl(reaction.emoji?.image)}
				alt="Avatar"
				width="100%"
				height="100%"
				onerror="this.style.visibility='hidden'"
			/>
			<span class="chatlog__reaction-count">{reaction.count}</span>
		</div>
	{/each}
</div>

<style>
	.chatlog__reaction {
		margin-right: 4px;
	}
	.chatlog__reaction.me {
		border: 1px solid #5561E9;
		background-color: #34374F;
	}
</style>