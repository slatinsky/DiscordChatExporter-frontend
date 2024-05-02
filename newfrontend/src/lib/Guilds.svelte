<!-- GUILDS MENU -->

<script lang="ts">
	import { checkUrl, copyTextToClipboard } from "../js/helpers"
    import { getGuildState } from "../js/stores/guildState.svelte";
    import { contextMenuItems } from "../js/stores/menuStore";
    import IconDCEF2 from "./icons/IconDCEF2.svelte";

	function onRightClick(e, id) {
        console.log("right click", id);
		$contextMenuItems = [
			{
				"name": "Copy guild ID",
				"action": () => {
					copyTextToClipboard(BigInt(id))
				}
			}
		]
	}

    let isMenuHidden = $state(false)
	const guildState = getGuildState()
</script>

<div class="guilds" class:hidden={isMenuHidden}>
	<div class="guild" class:selected={!guildState.guildId} on:click={e => guildState.changeGuildId(null)}>
		<div class="guild-selected-indicator" />
		<div class="home-guild"><IconDCEF2 /></div>
	</div>
	<hr>

	{#if guildState.guilds}
		{#each guildState.guilds as guild}
			<div class="guild" on:contextmenu|preventDefault={e=>onRightClick(e, guild._id)} class:selected={guildState.guildId === guild._id} on:click={e => guildState.changeGuildId(guild._id)}>
				<div class="guild-selected-indicator" />
				<img src={checkUrl(guild.icon)} alt={guild.name} on:error={e => (e.target.src = "/favicon.png")} />
			</div>
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

		padding: 9px;
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