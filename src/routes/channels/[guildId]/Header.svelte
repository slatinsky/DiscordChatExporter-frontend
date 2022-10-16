<script>
	import SearchFilter from './SearchFilter.svelte';

	export let channel;
	// export let messages;
	export let search;
	export let guild;
	export let found_messages;
	export let searched;
</script>

<section class="header-container">
	<div class="channel-header">
		<div class="channel-header__left">
			{#if channel}
				<div class="channel-name elipsis"># {channel.name}</div>
				{#if channel.topic}
					<div class="topic elipsis">| {channel.topic}</div>
				{/if}
			{/if}
			<div class="spacer" />
			<SearchFilter bind:found_messages bind:searched {guild} />
			<!-- <Search {messages} /> -->
		</div>
	</div>
</section>

<style>
	.header-container {
		background-color: #36393f;
		height: 100vh;
	}
	.channel-header__left {
		display: flex;
		flex-direction: row;
		align-items: center;

		gap: 15px;

		padding: 10px 20px;

		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.channel-name {
		font-size: 1.5rem;
		font-weight: 700;
	}

	.topic {
		font-size: 1rem;
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
