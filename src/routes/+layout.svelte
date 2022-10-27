<script>
	import './styles.css';

	export let data;
</script>



{#if data.failed}
	<div class="error">
		<h1>No chat exports found</h1>
		<p>
			Please move your DiscordChatExporter JSON+media exports to "/static/input/" folder and rerun
			"START_VIEWER.bat"
		</p>
	</div>
{:else}
	<div class="app">
		<div class="guilds">
			<a href="/">
				<div class="guild">
					<!-- if root path -->
					{#if !data.guildId}
						<div class="guild-selected" />
					{/if}
					<div class="home-guild">HOME</div>
				</div>
			</a>
			<!--        guild list-->
			{#if data.guilds}
				{#each Object.values(data.guilds) as guild}
					<a href="/channels/{guild.id}">
						<div class="guild">
							{#if data.guildId === guild.id}
								<div class="guild-selected" />
							{/if}
							<img src={guild.localFilePath} alt={guild.name} />
						</div>
					</a>
				{/each}
			{/if}
		</div>
		<div class="right">
			<!--        others-->
			<main>
				<slot />
			</main>
		</div>
	</div>
{/if}

<style>

    .error {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        text-align: center;
		padding: 2rem;
    }
	.app {
		display: grid;
		grid-template-columns: 70px 1fr;
		height: 100vh;
	}
	.guilds {
		background-color: #202225;
		height: 100%;
		overflow-y: auto;
	}

	.right {
		height: 100%;
	}

	img {
		width: 48px;
		height: 48px;
		margin: 5px 5px 5px 0px;
	}

	.home-guild {
		width: 48px;
		height: 48px;
		margin: 5px;
		background-color: #202225;
		border-radius: 50%;
		display: flex;
		justify-content: center;
		align-items: center;

		/* Border white circle */
		border-width: 1px;
		border-style: solid;
		border-color: #ffffff;

		font-size: small;
	}

	.guild {
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: center;
		gap: 10px;
	}

	.guild-selected {
		width: 10px;
		height: 40px;
		background-color: #ffffff;
		border-radius: 5px;
		position: absolute;
		left: -6px;
		z-index: 100;
	}
</style>
