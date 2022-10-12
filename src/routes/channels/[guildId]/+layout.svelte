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
					<a href="/channels/{data.guildId}/{channel.id}"># {channel.name}</a>
					{#if channel.threads}
						{#each channel.threads as thread}
								<!-- {thread.id} -->
								<br /><a href="/channels/{data.guildId}/{thread.id}" class="thread">
									<!-- svg -->
									<svg
										class="thread-svg-icon"
										width="8"
										height="8"
										viewBox="0 0 12 11"
										fill="none"
										aria-hidden="true"
										><path
											d="M11 9H4C2.89543 9 2 8.10457 2 7V1C2 0.447715 1.55228 0 1 0C0.447715 0 0 0.447715 0 1V7C0 9.20914 1.79086 11 4 11H11C11.5523 11 12 10.5523 12 10C12 9.44771 11.5523 9 11 9Z"
											fill="currentColor"
										/></svg
									>
									{thread.name}</a
								> 
						{/each}
					{/if}
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

	.thread {
		margin: 5px 15px 5px 30px;
		font-size: small;
		color: gray;
		text-decoration: none;
	}

	.thread:hover {
		color: white;
	}
/* 
	.channel:hover {
		background-color: #42474d;
	} */

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
