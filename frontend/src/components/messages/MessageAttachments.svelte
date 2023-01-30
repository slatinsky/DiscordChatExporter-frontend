<script lang="ts">
	import { checkUrl } from "src/js/helpers";
	import type { Asset } from "src/js/interfaces";
	import ImageGallery from "src/routes/channels/[guildId]/[channelId]/ImageGallery.svelte";
	export let attachments: Asset[] = [];
</script>

{#each attachments as attachment}
	{#if attachment.type == 'image'}
		<div class="chatlog__attachment">
			<ImageGallery asset={attachment} imgclass={"chatlog__attachment-media"} />
		</div>

	{:else if attachment.type == 'video'}
	<div class:media-spoiler={attachment.filenameWithoutHash.startsWith('SPOILER')}>
		<!-- title -->
		<div class="chatlog__attachment">
			<a href={checkUrl(attachment)} target="_blank">
				<div class="chatlog__attachment-media">
					<div class="chatlog__attachment-media-title">
						{attachment.filenameWithoutHash}
					</div>
				</div>
			</a>
		</div>
		<video class="chatlog__attachment-media" controls preload="metadata">
			<source src={checkUrl(attachment)} alt="{attachment.filenameWithoutHash}" title="Video: {attachment.filenameWithoutHash} ({attachment.sizeBytes} B)">
		</video>
	</div>
	{:else}
		<div class="chatlog__attachment">
			<a href={checkUrl(attachment)} target="_blank">
				<div class="chatlog__attachment-generic">
					<svg class="chatlog__attachment-generic-icon">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="24"
							height="24"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
							class="feather feather-file"
						>
							<path
								d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
							/>
							<polyline points="14 2 14 8 20 8" />
							<line x1="16" y1="13" x2="8" y2="13" />
							<line x1="16" y1="17" x2="8" y2="17" />
							<polyline points="10 9 9 9 8 9" />
						</svg>
					</svg>
					<div class="chatlog__attachment-generic-name">
						<a href={checkUrl(attachment)} target="_blank">
							{attachment.fileName}
						</a>
					</div>
					<div class="chatlog__attachment-generic-size">
						{Math.round(attachment.fileSizeBytes / 1024)} KB
					</div>
				</div>
			</a>
		</div>
		{#if attachment.type == 'audio'}
		<audio class="chatlog__attachment-media" controls preload="metadata">
			<source src="{checkUrl(attachment?.url?.url)}" alt="{attachment?.Description ?? 'Audio attachment'}" title="Audio: {attachment.fileName} ({attachment.fileSizeBytes} B)">
		</audio>
		{/if}
	{/if}
{/each}