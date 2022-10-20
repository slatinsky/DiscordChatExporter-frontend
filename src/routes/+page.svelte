<script>
	import { nameRenderer, timestampFormat } from './settingsStore';
	import { timestampRenderers } from './time';

	let testDate = '2020-09-16T11:04:47.215+00:00';
</script>

<!-- <div class="title">Select guild</div> -->

<div class="title">Settings</div>

<p>Name format</p>
<div class="radios">
	{#key $nameRenderer}
	<label>
		<input type="radio" name="nameRenderer" value={"nickname"} bind:group={$nameRenderer} />
		<span>Render nicknames (Deleted User)</span>
	</label>
	<label>
		<input type="radio" name="nameRenderer" value={"handle"} bind:group={$nameRenderer} />
		<span>Render handles (Deleted_User#0000)</span>
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

<style>
	.title {
		font-size: 28px;
		padding-top: 20px;
		padding-left: 20px;
	}

	.title2 {
		font-size: 32px;
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
