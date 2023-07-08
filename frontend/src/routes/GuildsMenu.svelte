<!-- GUILDS MENU -->

<script lang="ts">
	import { contextMenuItems } from "src/components/menu/menuStore";
	import { checkUrl, copyTextToClipboard } from "src/js/helpers";
	import type { Guild } from "../js/interfaces";
	export let guilds: Guild[] = [];
	export let selectedGuildId: string | null = null;

	function onRightClick(e, id) {
		$contextMenuItems = [
			{
				"name": "Copy guild ID",
				"action": () => {
					copyTextToClipboard(BigInt(id))
				}
			}
		]
	}
</script>

<div class="guilds">
	<a href="/">
		<div class="guild" class:selected={!selectedGuildId}>
			<!-- if root path -->
			<div class="guild-selected-indicator" />
			<div class="home-guild">HOME</div>
		</div>
	</a>
	<hr>
	<!--        guild list-->
	{#if guilds}
		{#each guilds as guild}
			<a href="/channels/{guild._id}">
				<div class="guild" on:contextmenu|preventDefault={e=>onRightClick(e, guild._id)} class:selected={selectedGuildId === guild._id}>
					<div class="guild-selected-indicator" />
					<img src={checkUrl(guild.icon)} alt={guild.name} on:error={e => (e.target.src = "/favicon.png")} />
				</div>
			</a>
		{/each}
	{/if}
</div>

<style>
	.guilds {
		background-color: var(--panel-guilds-bg);
		height: calc(100% - 14px);  /* - padding */
		overflow-y: auto;
		position: relative;

		padding: 7px 0 7px 0;
		scrollbar-width: none; /* hide scrollbar - Firefox */
	}

	.guilds::-webkit-scrollbar {
		display: none;  /* hide scrollbar - Safari and Chrome */
	}

	.guild img,
	.home-guild {
		margin: 5px 5px 3px 2px;
		border-radius: 50%;
		width: 48px;
		height: 48px;
		transition: border-radius 0.2s ease-in-out;
	}

	.guild.selected img,
	.guild:hover img,
	.guild.selected .home-guild,
	.guild:hover .home-guild {
		border-radius: 25%;
	}

	.home-guild {
		background-color: #313338;
		display: flex;
		justify-content: center;
		align-items: center;
		font-size: small;

		color: #dbdee1;
	}

	.guild:hover .home-guild,
	.guild.selected .home-guild {
		background-color: #5865f2;
		color: white;
	}

	hr {
		border: 0;
		height: 2px;
		background: #333;
		margin: 5px 20px
	}

	.guild {
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: center;
		gap: 10px;
	}

	.guild .guild-selected-indicator {
		position: absolute;
		left: -6px;
		width: 6px;
		height: 0px;
		background-color: var(--color-contrast);
		border-radius: 5px;
		z-index: 100;

		transition: height 0.2s ease-in-out;
	}

	.guild:hover .guild-selected-indicator {
		height: 20px;
		width: 10px;
		transition: width 0.2s ease-in-out;
	}

	.guild.selected .guild-selected-indicator {
		height: 40px;
		width: 10px;
		transition: height 0.2s ease-in-out;
	}


</style>