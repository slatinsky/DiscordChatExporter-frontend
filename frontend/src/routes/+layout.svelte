<script>
	import MemoryUsage from './channels/[guildId]/MemoryUsage.svelte';
	import { theme, hideSpoilers, font } from './settingsStore';
import './styles.css';

	export let data;

	theme.subscribe(value => {
		document.documentElement.setAttribute('data-theme', value);
	});

	hideSpoilers.subscribe(value => {
		document.documentElement.setAttribute('data-hidespoilers', value);
	});

	font.subscribe(value => {
		document.documentElement.setAttribute('data-font', value);
	});
</script>



{#if Object.values(data.guilds).length === 0}
	<div class="error">
		<h1>No chat exports found</h1>
		<p>
			Please close this app and "http-server" terminal, move your DiscordChatExporter JSON+media exports to "/exports/" folder and rerun
			"START_VIEWER.bat"
		</p>

		<small>If your exports are in the correct place and you still see this error, please open an issue on <a href="https://github.com/slatinsky/DiscordChatExporter-frontend/issues" target="_blank">GitHub</a>. Please check out command line window if you see any errors / crashes there</small>
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
	<MemoryUsage />
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
		background-color: var(--panel-guilds-bg);
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
		background-color: #00000099;
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
		background-color: var(--color-contrast);
		border-radius: 5px;
		position: absolute;
		left: -6px;
		z-index: 100;
	}
</style>
