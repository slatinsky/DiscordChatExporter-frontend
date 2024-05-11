<script lang="ts">
    import { checkUrl, humanFileSize } from "../../js/helpers";
    import type { Asset } from "../../js/interfaces";
    import MessageAttachmentTxt from "./MessageAttachmentTxt.svelte";
    import AudioPlayer from "../audioplayer/AudioPlayer.svelte";
    import MessageTiledImages from "./MessageTiledImages.svelte";
    import Icon from "../icons/Icon.svelte";
    import MessageVideo from "./MessageVideo.svelte";

	interface MyProps {
        attachments: Asset[];
    }
    let { attachments}: MyProps = $props();

	let imageAttachments = $derived(attachments.filter(a => a.type === 'image' || (a.type === 'unknown' && !a.filenameWithoutHash.includes('.'))));
	let otherAttachments = $derived(attachments.filter(a => a.type !== 'image' && (a.type !== 'unknown' || a.filenameWithoutHash.includes('.'))));

</script>

{#if imageAttachments.length > 0}
	<div class="image-attachments-wrapper">
		<MessageTiledImages images={imageAttachments} isAttachment={true}/>
	</div>
{/if}

<!-- unknown because attachment name can be extensionless -->
<div class="attachment-container">
	{#each otherAttachments as attachment}
		{@const attachmentExtension: string = attachment?.filenameWithoutHash.toLowerCase().split('.').pop() ?? 'invalid-fileextension'}
		{#if attachment.type == 'video'}
			<MessageVideo attachment={attachment} />
		{:else if ['txt'].includes(attachmentExtension)}
			<MessageAttachmentTxt attachment={attachment} />
		{:else}
			<div class="attachment-wrapper">
				<div class="attachment" style="width: 100%;">
					{#if ['pdf'].includes(attachmentExtension)}
						<Icon name="filetype/pdf" width={24} height={32} />
					{:else if ['zip', 'rar', '7z'].includes(attachmentExtension)}
						<Icon name="filetype/archive" width={24} height={32} />
					{:else if ['xls', 'xlsx', 'ods'].includes(attachmentExtension)}
						<Icon name="filetype/spreadsheet" width={24} height={32} />
					{:else if ['ppt', 'pptx', 'doc', 'docx'].includes(attachmentExtension)}
						<Icon name="filetype/document" width={24} height={32} />
					{:else if ['mp3', 'wav', 'flac', 'ogg'].includes(attachmentExtension)}
						<Icon name="filetype/audio" width={24} height={32} />
					{:else}
						<Icon name="filetype/unknown" width={24} height={32} />
					{/if}

					<div>
						<a class="attachment-filename" href={checkUrl(attachment)} target="_blank" rel="noreferrer">{attachment.filenameWithoutHash}</a>
						<div class="attachment-filesize">{humanFileSize(attachment.sizeBytes, 2)}</div>
					</div>
				</div>
				{#if attachment.type == 'audio'}
					<div style="width: 100%;padding: 0 15px 15px 15px; margin-top: -5px;">
						<AudioPlayer
							src="{checkUrl(attachment)}"
						></AudioPlayer>
					</div>
				{/if}

				<a class="download-attachment" href={checkUrl(attachment)} target="_blank" rel="noreferrer">
					<Icon name="other/download" width={20}/>
				</a>
			</div>
		{/if}
	{/each}
</div>

<style>
	.image-attachments-wrapper {
		max-width: 550px;
		width: 100%;
	}
	.attachment-container {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.attachment-wrapper {
		display: block;
		background-color: #2b2d31;
		max-width: 400px;
		border-radius: 10px;
		border: 1px solid #232428;

		position: relative;

		.download-attachment {
			position: absolute;
			top: -10px;
			right: -10px;
			cursor: pointer;
			background-color: #313338;
			width: 32px;
			height: 32px;
			border-radius: 5px;
			border: 1px solid #2b2d31;

			color: #B5BAC1;

			place-items: center;

			display: none;
		}

		.download-attachment:hover {
			background-color: #383b3f;
			color: #dadde0;
		}
	}
	.attachment-wrapper:hover .download-attachment {
		display: grid;
	}

	.attachment {
		padding: 16px;
		display: flex;
		gap: 8px;
	}
	:global(.attachment svg) {
		width: 24px;
		height: 40px;
	}

	.attachment-filename {
		color: #00a8fc;
		font-size: 16px;
		font-weight: 400;
		text-decoration: none;
	}
	.attachment-filename:hover {
		text-decoration: underline;
	}

	.attachment-filesize {
		color: #80848e;
		font-size: 12px;
		font-weight: 400px;
	}
</style>