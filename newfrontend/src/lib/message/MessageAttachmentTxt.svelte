<script lang="ts">
	import { onMount } from "svelte";
    import { checkUrl, humanFileSize } from "../../js/helpers";
    import type { Asset } from "../../js/interfaces";

	interface MyProps {
        attachment: Asset;
    }
    let { attachment}: MyProps = $props();

	let messageContent: null | string = $state(null)
	let isExpanded: boolean = $state(false)

	let messagePreview: null | string = $derived.by(() => {
		if (messageContent == null) {
			return null
		}
		let lines = messageContent.split('\n')
		return lines.slice(0, 9).join('\n')
	})
	let messageExpanded: null | string = $derived.by(() => {
		if (messageContent == null) {
			return null
		}
		let lines = messageContent.split('\n')
		let messageExpanded = lines.slice(0, 100).join('\n')
		if (lines.length > 100) {
			messageExpanded += `\n... (${lines.length - 100} lines left)`
		}
		return messageExpanded
	})
	let canExpand = $derived(messagePreview !== messageExpanded)  // if the message is too long to show in preview
	let isError = $state(false)

	onMount(async() => {
		let url = checkUrl(attachment)

		try {
			const response = await fetch(url);
			if (!response.ok) {
				console.error('HTTP-Error: ' + response.status);
				isError = true
				return;
			}
			messageContent = await response.text();
		} catch (error) {
			console.error('Fetch Error: ', error);
			isError = true
		}
	})

	const CHEVRON_ICON_DOWN = `<svg aria-hidden="true" role="img" width="24" height="24" fill="none" viewBox="0 0 24 24"><path fill="currentColor" d="M5.3 9.3a1 1 0 0 1 1.4 0l5.3 5.29 5.3-5.3a1 1 0 1 1 1.4 1.42l-6 6a1 1 0 0 1-1.4 0l-6-6a1 1 0 0 1 0-1.42Z" class=""></path></svg>`
	const CHEVRON_ICON_UP = `<svg aria-hidden="true" role="img" width="24" height="24" fill="none" viewBox="0 0 24 24"><path fill="currentColor" d="M5.3 14.7a1 1 0 0 0 1.4 0L12 9.42l5.3 5.3a1 1 0 0 0 1.4-1.42l-6-6a1 1 0 0 0-1.4 0l-6 6a1 1 0 0 0 0 1.42Z" class=""></path></svg>`
	const DOWNLOAD_ICON = `<svg aria-hidden="true" role="img" width="24" height="24" fill="none" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2a1 1 0 0 1 1 1v10.59l3.3-3.3a1 1 0 1 1 1.4 1.42l-5 5a1 1 0 0 1-1.4 0l-5-5a1 1 0 1 1 1.4-1.42l3.3 3.3V3a1 1 0 0 1 1-1ZM3 20a1 1 0 1 0 0 2h18a1 1 0 1 0 0-2H3Z" class=""></path></svg>`
</script>

{#if isError}
	<p class="error">{attachment.filenameWithoutHash} - Error loading attachment txt preview</p>
{:else if messageContent == null}
	<p class="loading">{attachment.filenameWithoutHash} - Loading attachment txt preview...</p>
{:else}
	<div class="wrapper">
		{#if isExpanded}
			<pre class="message-txt">{messageExpanded}</pre>
		{:else}
			<pre class="message-txt">{messagePreview}</pre>
		{/if}
		<div class="footer">
			{#if canExpand}
				<button class="footer-expandcollapse" onclick={()=>isExpanded = !isExpanded}>
					{#if isExpanded}
						{@html CHEVRON_ICON_UP} <span>Collapse</span>
					{:else}
						{@html CHEVRON_ICON_DOWN} <span>Expand</span>
					{/if}
				</button>
			{:else}
				<div></div>
			{/if}
			<div class="footer-right">
				<div>{attachment.filenameWithoutHash}</div>
				<div class="filesize">{humanFileSize(attachment.sizeBytes, 0)}</div>
				<a href={checkUrl(attachment)} target="_blank" rel="noreferrer">
					<div>{@html DOWNLOAD_ICON}</div>
				</a>
			</div>
		</div>
	</div>
{/if}



<style>
	.error {
		color: red;
		font-size: 14px;
	}
	.loading {
		color: #b5bac1;
		font-size: 14px;
	}

	.wrapper {
		max-width: 550px;
	}

	.message-txt {
		background-color: #2B2D31;
		border: 1px solid #232428;
		border-radius: 8px 8px 0 0;
		width: 100%;
		min-height: 132px;
		text-wrap: wrap;
		padding: 16px;
		overflow-y: hidden;
		margin: 8px 0 0 0;
		font-size: 14px;
	}

	.footer {
		background-color: #2B2D31;
		border: 1px solid #232428;
		border-radius: 0 0 8px 8px;
		width: 100%;
		height: 40px;
		padding: 0 16px;

		display: flex;
		flex-direction: row;
		gap: 5px;
		justify-content: space-between;
		align-items: center;

		color: #b5bac1;
		font-size: 14px;
	}

	.footer-expandcollapse {
		display: flex;
		gap: 5px;
		align-items: center;
		cursor: pointer;
	}
	.footer .footer-right {
		display: flex;
		gap: 5px;
		align-items: center;
	}

	.filesize {
		color: #4e5058;
	}

	a {
		color: #b5bac1;
	}

	a:hover {
		color: #d8dbdd;
	}
</style>