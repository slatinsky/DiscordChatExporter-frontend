<script lang="ts">
	import { checkUrl, humanFileSize } from "src/js/helpers";
	import type { Asset } from "src/js/interfaces";
	import ImageGallery from "src/routes/channels/[guildId]/[channelId]/ImageGallery.svelte";
	import IconFilePdf from "../icons/IconFilePdf.svelte";
	import IconFileDocument from "../icons/IconFileDocument.svelte";
	import IconFIleArchive from "../icons/IconFIleArchive.svelte";
	import IconFileSpreadsheet from "../icons/IconFileSpreadsheet.svelte";
	import IconFileUnknown from "../icons/IconFileUnknown.svelte";
	import MessageAttachmentTxt from "./MessageAttachmentTxt.svelte";
	export let attachments: Asset[] = [];

</script>

{#each attachments as attachment}
	<!-- unknown because attachment name can be extensionless -->
	{#if attachment.type == 'image' || (attachment.type == 'unknown' && !attachment.filenameWithoutHash.includes('.'))}
		<div class="chatlog__attachment">
			<ImageGallery asset={attachment} imgclass={"message-image"} />
		</div>
	{:else if attachment.type == 'video'}
	<div class:media-spoiler={attachment.filenameWithoutHash.startsWith('SPOILER')}>
		<!-- video title -->
		<!-- {attachment.filenameWithoutHash} -->
		<video class="message-video" controls preload="metadata">
			<source src={checkUrl(attachment)} alt="{attachment.filenameWithoutHash}" title="Video: {attachment.filenameWithoutHash} ({Math.round(attachment.sizeBytes / 1024)} KB)">
		</video>
	</div>
	{:else if attachment.type == 'audio'}
		<audio class="" controls preload="metadata">
			<source src="{checkUrl(attachment)}" alt="{attachment?.filenameWithoutHash ?? 'Audio attachment'}" title="Audio: {attachment.filenameWithoutHash} ({Math.round(attachment.sizeBytes / 1024)} KB)">
		</audio>
	{:else if attachment.extension == 'txt'}
		<MessageAttachmentTxt attachment={attachment} />
	{:else}
		<a href={checkUrl(attachment)} target="_blank" class="attachment-wrapper" rel="noreferrer">
			<div class="attachment">
				{#if attachment?.filenameWithoutHash.toLowerCase().endsWith('.pdf')}
					<IconFilePdf />
				{:else if ['zip', 'rar', '7z'].includes(attachment?.filenameWithoutHash.toLowerCase().split('.').pop())}
					<IconFIleArchive />
				{:else if ['xls', 'xlsx', 'ods'].includes(attachment?.filenameWithoutHash.toLowerCase().split('.').pop())}
					<IconFileSpreadsheet />
				{:else if ['ppt', 'pptx', 'doc', 'docx'].includes(attachment?.filenameWithoutHash.toLowerCase().split('.').pop())}
					<IconFileDocument />
				{:else}
					<IconFileUnknown />
				{/if}
				<div>
					<div class="attachment-filename">{attachment.filenameWithoutHash}</div>
					<div class="attachment-filesize">{humanFileSize(attachment.sizeBytes, 2)}</div>
				</div>
			</div>
		</a>
	{/if}
{/each}

<style>
	audio {
		max-width: 80%;
		width: 700px;
	}

	.attachment-wrapper {
		display: block;
		background-color: #2b2d31;
		max-width: 400px;
		border-radius: 10px;
		border: 1px solid #232428;
	}

	.attachment {
		padding: 16px;
		display: flex;
		gap: 8px;
	}
	:global(.attachment svg) {
		width: 30px;
		height: 40px;
	}

	.attachment-filename {
		color: #00a8fc;
		font-size: 16px;
		font-weight: 400;
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