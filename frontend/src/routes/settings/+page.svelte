<script>
	import { nameRenderer, timestampFormat, developerMode, theme, online, linkHandler, channelScrollPosition, hideSpoilers, font } from '../settingsStore';
	import { timestampRenderers } from '../../js/time';
	import RadioButton from '../../components/settings/RadioButton.svelte';
	import RadioGroup from '../../components/settings/RadioGroup.svelte';

	let testDate = '2020-09-16T11:04:47.215+00:00';

	let selectedTab = 'appearance';
</script>

<svelte:head>
    <title>DiscordChatExporter frontend</title>
    <meta name="description" content="View your JSON DiscordChatExporter exports as if you were using Discord interface"/>
</svelte:head>


<div class="container">
	<div class="tabs">
		<div class="category">App settings</div>
		<div class="tab" class:selected={selectedTab == "appearance"} on:click={() => selectedTab = "appearance"}>Appearance</div>
		<div class="tab" class:selected={selectedTab == "privacy"} on:click={() => selectedTab = "privacy"}>Privacy & Safety</div>
		<div class="tab" class:selected={selectedTab == "accessibility"} on:click={() => selectedTab = "accessibility"}>Accessibility</div>

		<hr>

		<div class="category">Advanced settings</div>
		<div class="tab" class:selected={selectedTab == "advanced"} on:click={() => selectedTab = "advanced"}>Advanced</div>
	</div>

	<div class="settings">

		<a href="/" class="close-btn">
			<svg role="img" width="18" height="18" viewBox="0 0 24 24"><path fill="currentColor" d="M18.4 4L12 10.4L5.6 4L4 5.6L10.4 12L4 18.4L5.6 20L12 13.6L18.4 20L20 18.4L13.6 12L20 5.6L18.4 4Z"></path></svg>
		</a>

		{#if selectedTab == "appearance"}
			<div class="title">Appearance</div>

			<RadioGroup
				title={"Name format"}
			>
				<RadioButton
					title={"Display name"}
					name={"nameRenderer"}
					value={"nickname"}
					bind:group={$nameRenderer}
				/>

				<RadioButton
					title={"Username"}
					name={"nameRenderer"}
					value={"handle"}
					bind:group={$nameRenderer}
				/>

				<RadioButton
					title={"Both"}
					name={"nameRenderer"}
					value={"both"}
					bind:group={$nameRenderer}
				/>
			</RadioGroup>

			<hr>

			<RadioGroup
				title={"Timestamp format"}
			>
				{#each timestampRenderers as renderer, i}
					<RadioButton
						title={renderer(testDate)}
						name={"timestampRenderers"}
						value={i}
						bind:group={$timestampFormat}
					/>
				{/each}
			</RadioGroup>

			<hr>

			<RadioGroup
				title={"Default scroll position"}
				description={"For channels/threads/forum posts"}
			>
				<RadioButton
					title={"Bottom"}
					name={"channelScrollPosition"}
					value={"bottom"}
					bind:group={$channelScrollPosition}
				/>

				<RadioButton
					title={"Top"}
					name={"channelScrollPosition"}
					value={"top"}
					bind:group={$channelScrollPosition}
				/>
			</RadioGroup>

			<hr>

			<RadioGroup
				title={"Theme"}
				description={"Only dark theme works correctly at the moment"}
			>
				<RadioButton
					title={"Dark"}
					name={"theme"}
					value={"dark"}
					bind:group={$theme}
				/>

				<RadioButton
					title={"Black [Work in progress]"}
					name={"theme"}
					value={"black"}
					bind:group={$theme}
				/>

				<RadioButton
					title={"White [Work in progress]"}
					name={"theme"}
					value={"white"}
					bind:group={$theme}
				/>
			</RadioGroup>
		{/if}

		{#if selectedTab == "privacy"}
			<div class="title">Privacy & Safety</div>

			<RadioGroup
				title={"Online mode"}
				description={"If enabled, this will allow you to view emojis, stickers, attachments, embeds, etc. that you don't have downloaded"}
			>
				<RadioButton
					title={"Yes"}
					name={"online"}
					value={true}
					bind:group={$online}
				/>
				<RadioButton
					title={"No"}
					name={"online"}
					value={false}
					bind:group={$online}
				/>


			</RadioGroup>

			<hr>

			<RadioGroup
				title={"Hide/blur spoilers"}
			>
				<RadioButton
					title={"Yes"}
					name={"hideSpoilers"}
					value={true}
					bind:group={$hideSpoilers}
				/>

				<RadioButton
					title={"No"}
					name={"hideSpoilers"}
					value={false}
					bind:group={$hideSpoilers}
				/>
			</RadioGroup>

		{/if}

		{#if selectedTab == "accessibility"}
			<div class="title">Accessibility</div>

			<RadioGroup
				title={"Discord font"}
			>
				<RadioButton
					title={"gg sans (new discord font)"}
					name={"font"}
					value={"ggsans"}
					bind:group={$font}
				/>

				<RadioButton
					title={"Whitney (old discord font)"}
					name={"font"}
					value={"whitney"}
					bind:group={$font}
				/>

				<RadioButton
					title={"Arial"}
					name={"font"}
					value={"arial"}
					bind:group={$font}
				/>

				<RadioButton
					title={"Times New Roman"}
					name={"font"}
					value={"timesnewroman"}
					bind:group={$font}
				/>

				<RadioButton
					title={"Comic Sans"}
					name={"font"}
					value={"comicsans"}
					bind:group={$font}
				/>
			</RadioGroup>
		{/if}


		{#if selectedTab == "advanced"}
			<div class="title">Advanced</div>

			<!-- "discord://" URL protocol for invoking application has to be registered -->
			<RadioGroup
				title={"Open discord links"}
				description={"Right click message to open in Discord"}
			>
				<RadioButton
					title={"In browser"}
					name={"linkHandler"}
					value={"browser"}
					bind:group={$linkHandler}
				/>

				<RadioButton
					title={"In discord app"}
					name={"linkHandler"}
					value={"app"}
					bind:group={$linkHandler}
				/>
			</RadioGroup>

			<hr>
			<RadioGroup
				title={"Show memory usage"}
			>
				<RadioButton
					title={"Disabled"}
					name={"developerMode"}
					value={false}
					bind:group={$developerMode}
				/>
				<RadioButton
					title={"Enabled"}
					name={"developerMode"}
					value={true}
					bind:group={$developerMode}
				/>
			</RadioGroup>
		{/if}
	</div>
</div>

<style>
	.container {
		display: grid;
		grid-template-columns: 1fr 2fr;
		gap: 20px;
		height: 100vh;
		/* padding: 20px auto; */
	}
	.tabs {
		background-color: #2b2d31;
		display: flex;
		flex-direction: column;
		gap: 2px;
		padding-top: 30px;
		padding-left: 30px;
		padding-right: 10px;
		align-items: flex-end;
	}

	.tab {
		width: 200px;
		border-radius: 5px;
		cursor: pointer;

		padding-top: 6px;
		padding-bottom: 6px;
		padding-left: 10px;
		margin-bottom: 2px;
		border-radius: 4px;

		position: relative;
		font-size: 16px;
		line-height: 20px;
		cursor: pointer;
		font-weight: 500;

		color: #b5bac1;
	}

	.tab:hover
	{
		background-color: #35373c;
		color: #dbdee1;
	}

	.tab.selected {
		background-color: #404249;
		color: white;
	}

	.tabs .category {
		width: 200px;
        color:#949ba4;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .02em;
        font-size: 12px;
        line-height: 16px;
		margin-bottom: 5px;
    }

	.tabs hr {
        border: 0;
        height: 1px;
        background: #3b3d44;
        margin: 5px 30px 15px 0;
		width: 172px;
    }

	.settings {
		position: relative;
		padding-top: 30px;
		background-color: #313338;
		margin-left: 35px;
		margin-right: 35px;
		max-width: 700px;
	}

	.close-btn {
		position: absolute;
		top: 30px;
		left: 730px;
		cursor: pointer;

		display: grid;
		place-items: center;

		width: 32px;
		height: 32px;

		border: 2px solid #b5bac1;
		border-radius: 50%;
	}

	.close-btn svg {
		color: #b5bac1;
	}

	.close-btn:hover {
		border: 2px solid #dbdee1;
	}

	.close-btn:hover svg {
		color: #dbdee1;
	}


	.settings .title {
		font-weight: 600;
		font-size: 20px;
		line-height: 24px;
		color: #f2f3f5;
		padding-bottom: 20px;
	}

	.settings hr {
        border: 0;
        height: 1px;
        background: #3f4147;
        margin: 30px 0 40px 0;
    }
</style>
