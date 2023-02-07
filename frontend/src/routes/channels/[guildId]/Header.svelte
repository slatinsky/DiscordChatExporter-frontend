<script lang="ts">
	import type { Channel } from 'src/js/interfaces';
	import IconChannel from '../../../components/icons/IconChannel.svelte';
	import SearchFilter from '../../../components/search/SearchFilter.svelte';

	export let channel: Channel | null = null;
	export let thread: Channel | null = null;
	export let guildId: string;
</script>

<section class="header-container">
	<div class="channel-header">
		<div class="channel-header__left">
			{#if channel !== null}
				<IconChannel />
				<a href={`/channels/${guildId}/${channel._id}`}>
					<div class="channel-name elipsis"> {channel.name}</div>
				</a>
				{#if thread === null && channel.topic !== null}
					<div class="divider">|</div>
					<div class="topic elipsis">{channel.topic}</div>
				{/if}
			{/if}
			{#if thread !== null}
					<div class="divider">|</div>
					<IconChannel />
					<a href={`/channels/${guildId}/${thread._id}`}>
						<div class="channel-name elipsis"> {thread.name}</div>
					</a>
					{#if thread.topic !== null}
						<div class="divider">|</div>
						<div class="topic elipsis">{thread.topic}</div>
					{/if}
				{/if}
			<div class="spacer" />
			<SearchFilter {guildId} />
		</div>
	</div>
</section>

<style>
	.header-container {
		background-color: var(--panel-messages-bg);
		height: 100vh;
	}
	.channel-header__left {
		display: flex;
		flex-direction: row;
		align-items: center;

		gap: 10px;

		padding: 10px 20px;

		/* border-bottom: 1px solid rgba(255, 255, 255, 0.1); */
		/*bottom shadow*/
		box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.1);
	}

	.channel-name {
		font-size: 17px;
		font-weight: 700;
		color: var(--color-contrast);
	}

	:global(.channel-name svg) {
		margin-top: 5px;
	}

	.topic {
		font-size: 14px;
		font-weight: 400;
		color: var(--header-icon);
	}

	.divider {
		font-size: 24px;
		font-weight: 400;
		color: gray;
	}
	.elipsis {
		display: -webkit-box;
		-webkit-line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.info-text {
		font-size: 32px;
		padding-top: 20px;
		padding-left: 20px;
	}

	.spacer {
		flex-grow: 1;
	}
</style>
