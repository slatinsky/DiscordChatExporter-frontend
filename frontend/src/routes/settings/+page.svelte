<script>
	import { nameRenderer, timestampFormat, developerMode, theme, online, linkHandler, channelScrollPosition, hideSpoilers, font } from '../settingsStore';
	import { timestampRenderers } from '../../js/time';

	let testDate = '2020-09-16T11:04:47.215+00:00';
</script>

<svelte:head>
    <title>DiscordChatExporter frontend</title>
    <meta name="description" content="View your JSON DiscordChatExporter exports as if you were using Discord interface"/>
</svelte:head>

<div class="title">Settings</div>

<p>Name format</p>
<div class="radios">
	{#key $nameRenderer}
	<label>
		<input type="radio" name="nameRenderer" value={"nickname"} bind:group={$nameRenderer} />
		<span>Nickname (Deleted User) [Work in progress]</span>
	</label>
	<label>
		<input type="radio" name="nameRenderer" value={"handle"} bind:group={$nameRenderer} />
		<span>Name with handle (Deleted_User#0000)</span>
	</label>
	<label>
		<input type="radio" name="nameRenderer" value={"both"} bind:group={$nameRenderer} />
		<span>Both (Deleted User (Deleted_User#0000)) [Work in progress]</span>
	</label>
	{/key}
</div>

<p>Timestamp format (original "{testDate}")</p>
<div class="radios">
	{#each timestampRenderers as renderer, i}
		<label>
			<input type="radio" name="timestampRenderers" value={i} bind:group={$timestampFormat} />
			<span>{renderer(testDate)}</span>
		</label>
	{/each}
</div>

<p>Default scroll position (for channels/threads/forum posts)</p>
<div class="radios">
	{#key $channelScrollPosition}
	<label>
		<input type="radio" name="channelScrollPosition" value={"top"} bind:group={$channelScrollPosition} />
		<span>Top</span>
	</label>
	<label>
		<input type="radio" name="channelScrollPosition" value={"bottom"} bind:group={$channelScrollPosition} />
		<span>Bottom</span>
	</label>
	{/key}
</div>

<p>Discord font</p>
<div class="radios">
	{#key $font}
	<label>
		<input type="radio" name="font" value={"ggsans"} bind:group={$font} />
		<span>gg sans (new discord font)</span>
	</label>
	<label>
		<input type="radio" name="font" value={"whitney"} bind:group={$font} />
		<span>Whitney (old discord font)</span>
	</label>
	<label>
		<input type="radio" name="font" value={"arial"} bind:group={$font} />
		<span>Arial</span>
	</label>
	<label>
		<input type="radio" name="font" value={"timesnewroman"} bind:group={$font} />
		<span>Times New Roman</span>
	</label>
	<label>
		<input type="radio" name="font" value={"comicsans"} bind:group={$font} />
		<span>Comic Sans</span>
	</label>
	{/key}
</div>


<p>Show memory usage</p>
<div class="radios">
	{#key $developerMode}
	<label>
		<input type="radio" name="developerMode" value={true} bind:group={$developerMode} />
		<span>Enabled</span>
	</label>
	<label>
		<input type="radio" name="developerMode" value={false} bind:group={$developerMode} />
		<span>Disabled</span>
	</label>
	{/key}
</div>

<p>Open discord links (right click message to open in Discord)</p>
<div class="radios">
	{#key $linkHandler}
	<label>
		<input type="radio" name="linkHandler" value={"browser"} bind:group={$linkHandler} />
		<span>In browser</span>
	</label>
	<label>
		<input type="radio" name="linkHandler" value={"app"} bind:group={$linkHandler} />
		<!-- "discord://" URL protocol for invoking application has to be registered -->
		<span>In discord app</span>
	</label>
	{/key}
</div>

<p>Fetch assets from remote servers</p>
<div class="radios">
	{#key $online}
	<label>
		<input type="radio" name="online" value={false} bind:group={$online} />
		<span>Never - view assets offline only</span>
	</label>
	<label>
		<input type="radio" name="online" value={true} bind:group={$online} />
		<span>If local assets don't exist</span>
	</label>
	{/key}
</div>

<p>Hide/blur spoilers</p>
<div class="radios">
	{#key $hideSpoilers}
	<label>
		<input type="radio" name="hideSpoilers" value={true} bind:group={$hideSpoilers} />
		<span>Yes</span>
	</label>
	<label>
		<input type="radio" name="hideSpoilers" value={false} bind:group={$hideSpoilers} />
		<span>No</span>
	</label>
	{/key}
</div>

<p>Theme</p>
<div class="radios">
	{#key $theme}
	<label>
		<input type="radio" name="theme" value={"dark"} bind:group={$theme} />
		<span>Dark</span>
	</label>
	<label>
		<input type="radio" name="theme" value={"black"} bind:group={$theme} />
		<span>Black [Work in progress]</span>
	</label>
	<label>
		<input type="radio" name="theme" value={"white"} bind:group={$theme} />
		<span>White [Work in progress]</span>
	</label>
	{/key}
</div>

<style>
	.title {
		font-size: 28px;
		padding-top: 20px;
		padding-left: 20px;
	}

	.radios {
		display: flex;
		flex-direction: column;
		gap: 10px;
		padding-left: 20px;
	}

	p {
		padding-left: 20px;
	}
</style>
