<script>
	export let data
</script>

<div class="container">
	<div class="txt">Select channel</div>
</div>

<svelte:head>
    <title>{data.guilds[data.guildId].name} | DiscordChatExporter frontend</title>
    <meta name="description" content="Svelte demo app"/>
</svelte:head>

<style>
	.container {
		background-color: #36393f;
		height: 100vh;
	}

	.txt {
		font-size: 32px;
		padding-top: 20px;
		padding-left: 20px;
	}
</style>
