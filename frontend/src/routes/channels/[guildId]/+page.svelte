<script>
	export let data
</script>

<div class="container">
	<div class="txt">Select channel</div>
</div>

<svelte:head>
    <title>{data.guild.name} | DiscordChatExporter frontend</title>
</svelte:head>

<style>
	.container {
		background-color: var(--panel-messages-bg);
		height: 100%;
	}
</style>
