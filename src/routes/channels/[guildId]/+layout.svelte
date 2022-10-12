<script>
	export let data;
</script>

<div class="columns">
	<div class="channels">
		<div class="guild-name">{data.guilds[data.guildId].name}</div>
		{#each Object.values(data.guild.categories) as category}
			<div>{category.name}</div>
			{#each category.channelIds as channel}
				<div class="channel">
					<a href="/channels/{data.guildId}/{channel.id}">#{channel.name}</a>
				</div>
			{/each}
		{/each}
	</div>
	<div>
		<slot />
	</div>
</div>

<style>
	.channel {
		margin: 5px 15px;
	}

	.channel:hover {
		background-color: #42474d;
	}

	.channels {
		display: flex;
		flex-direction: column;
		margin: 10px 15px;
		overflow-y: auto;
	}

	.columns {
		display: grid;
		grid-template-columns: 250px auto;
		flex-direction: row;
		background-color: #2f3136;
		height: 100vh;
	}

	.guild-name {
		font-size: 20px;
		font-weight: 600;
	}

	.category-name {
		font-size: 16px;
		font-weight: 600;
		margin: 15px 0 0px 0;
	}
</style>
