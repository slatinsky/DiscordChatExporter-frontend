<script>
	import Search from './[channelId]/Search.svelte';

	export let channel;
	// export let messages;
</script>


{#if channel}
<section>
	<div class="channel-header">
		<div class="channel-header__left">
			<div class="channel-name elipsis"># {channel.name}</div>
            {#if channel.topic}
			    <div class="topic elipsis">| {channel.topic}</div>
            {/if}
			<!-- <Search {messages} /> -->
		</div>
	</div>
</section>
{:else}
	<div class="info-text">Channel/Thread not exported</div>
{/if}

<style>
	.channel-header__left {
		display: flex;
		flex-direction: row;
		align-items: center;

		gap: 15px;

		padding: 10px 20px;
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
</style>
