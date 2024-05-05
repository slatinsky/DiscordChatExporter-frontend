<script lang="ts">
    import { checkUrl, humanFileSize } from "../../js/helpers";
    import type { Asset } from "../../js/interfaces";
    import ImageGallery from "../ImageGallery.svelte";
    import IconFIleArchive from "../icons/IconFIleArchive.svelte";
    import IconFileDocument from "../icons/IconFileDocument.svelte";
    import IconFilePdf from "../icons/IconFilePdf.svelte";
    import IconFileSpreadsheet from "../icons/IconFileSpreadsheet.svelte";
    import IconFileUnknown from "../icons/IconFileUnknown.svelte";
    import MessageAttachmentTxt from "./MessageAttachmentTxt.svelte";
    import AudioPlayer from "../audioplayer/AudioPlayer.svelte";
    import IconFileAudio from "../icons/IconFileAudio.svelte";
    import IconAttachmentDownload from "../icons/IconAttachmentDownload.svelte";

    export let attachments: Asset[]
</script>

<!-- unknown because attachment name can be extensionless -->
<div class="attachment-container">
	{#each attachments as attachment}
		{@const attachmentExtension: string = attachment?.filenameWithoutHash.toLowerCase().split('.').pop() ?? 'invalid-fileextension'}
		{#if attachment.type == 'image' || (attachment.type == 'unknown' && !attachment.filenameWithoutHash.includes('.'))}
			<ImageGallery asset={attachment} imgclass={"message-image"} />
		{:else if attachment.type == 'video'}
			<div class:media-spoiler={attachment.filenameWithoutHash.startsWith('SPOILER')}>
			<!-- video title -->
			<!-- {attachment.filenameWithoutHash} -->
			<video class="message-video" controls preload="metadata">
				<source src={checkUrl(attachment)} alt="{attachment.filenameWithoutHash}" title="Video: {attachment.filenameWithoutHash} ({Math.round(attachment.sizeBytes / 1024)} KB)">
			</video>
			</div>
		{:else if ['txt'].includes(attachmentExtension)}
			<MessageAttachmentTxt attachment={attachment} />
		{:else}
			<div class="attachment-wrapper">
				<div class="attachment" style="width: 100%;">
					{#if ['pdf'].includes(attachmentExtension)}
						<IconFilePdf />
					{:else if ['zip', 'rar', '7z'].includes(attachmentExtension)}
						<IconFIleArchive />
					{:else if ['xls', 'xlsx', 'ods'].includes(attachmentExtension)}
						<IconFileSpreadsheet />
					{:else if ['ppt', 'pptx', 'doc', 'docx'].includes(attachmentExtension)}
						<IconFileDocument />
					{:else if ['mp3', 'wav', 'flac', 'ogg'].includes(attachmentExtension)}
						<IconFileAudio />
					{:else}
						<IconFileUnknown />
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
					<IconAttachmentDownload width={20}/>
				</a>
			</div>
		{/if}
	{/each}
</div>

<style>
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

	:global(.message-image) {
		max-width: 80%;
		max-height: 500px;
		vertical-align: top;
		border-radius: 8px;
		object-position:left;
		width: auto;
		height: auto;
	}
</style>