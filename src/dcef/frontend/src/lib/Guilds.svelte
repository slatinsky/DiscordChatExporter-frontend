<!-- GUILDS MENU -->

<script lang="ts">
	import { checkUrl, copyTextToClipboard } from "../js/helpers"
    import { getGuildState } from "../js/stores/guildState.svelte";
    import { contextMenuItems } from "../js/stores/menuStore";
    import { linkHandler } from "../js/stores/settingsStore.svelte";
    import Icon from "./icons/Icon.svelte";

	function onRightClick(e, id) {
        console.log("right click", id);
		$contextMenuItems = [
			{
				"name": `Open guild in discord ${$linkHandler === 'app' ? "app" : "web"}`,
				"action": () => {
					window.open(($linkHandler === "app" ? "discord://" : "") + `https://discord.com/channels/${BigInt(id)}`,'_blank')
				}
			},
			{
				"name": "Copy server ID",
				"action": () => {
					copyTextToClipboard(BigInt(id))
				}
			}
		]
	}

	const guildState = getGuildState()

	async function changeGuildId(guildId: string | null) {
		await guildState.changeGuildId(guildId)
		await guildState.pushState()
	}
</script>

<div class="guilds">
	<div class="guild" class:selected={!guildState.guildId} on:click={e => changeGuildId(null)}>
		<div class="guild-selected-indicator" />
		<div class="home-guild"><Icon name="dcef/filled" width={30} /></div>
	</div>
	<hr>

	{#if guildState.guilds}
		{#each guildState.guilds as guild}
			{#if guild._id !== "000000000000000000000000"}
				<div class="guild" on:contextmenu|preventDefault={e=>onRightClick(e, guild._id)} class:selected={guildState.guildId === guild._id} on:click={e => changeGuildId(guild._id)}>
					<div class="guild-selected-indicator" />
					<img src={checkUrl(guild.icon)} alt={guild.name} on:error={e => (e.target.src = "/favicon.png")} />
				</div>
			{/if}
		{/each}
	{/if}
</div>

<style>
	.guilds {
		width: 100%;
        height: 100%;
		cursor: pointer;

		overflow-y: auto;
		position: relative;

		padding: 0 4px 7px 0;
		scrollbar-width: none; /* hide scrollbar - Firefox */

		transition: left 0.2s ease-in-out;
		left: 0px
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
		margin: 5px 16px 5px 20px;
	}

	.guild {
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: center;
		gap: 10px;
        margin-left: 10px;
	}

	.guild .guild-selected-indicator {
        background-color: white;
		position: absolute;
		left: -6px;
		width: 6px;
		height: 0px;
		border-radius: 5px;

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