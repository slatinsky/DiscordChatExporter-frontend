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
		<div class="guild">
			<!-- if root path -->
			{#if !selectedGuildId}
				<div class="guild-selected" />
			{/if}
			<div class="home-guild">HOME</div>
		</div>
	</a>
	<!--        guild list-->
	{#if guilds}
		{#each guilds as guild}
			<a href="/channels/{guild._id}">
				<div class="guild" on:contextmenu|preventDefault={e=>onRightClick(e, guild._id)}>
					{#if selectedGuildId === guild._id}
						<div class="guild-selected" />
					{/if}
					<img src={checkUrl(guild.icon)} alt={guild.name} on:error={e => (e.target.src = "/favicon.png")} />
				</div>
			</a>
		{/each}
	{/if}
</div>

<style>
	.guilds {
		background-color: var(--panel-guilds-bg);
		height: 100%;
		overflow-y: auto;
		position: relative;
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