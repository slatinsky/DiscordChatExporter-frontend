<script lang="ts">
	import { checkUrl } from "src/js/helpers";
	import type { Embed } from "src/js/interfaces";
	import ImageGallery from "src/routes/channels/[guildId]/[channelId]/ImageGallery.svelte";
	import MessageMarkdown from "./MessageMarkdown.svelte";

	export let embeds: Embed[];
</script>

{#each embeds as embed}
	<div class="chatlog__embed">
		<!-- @{/* Color pill */} -->
		{#if embed.color}
			<div class="chatlog__embed-color-pill" style="background-color: {embed.color}"></div>
		{:else}
			<div class="chatlog__embed-color-pill chatlog__embed-color-pill--default"></div>
		{/if}

		<div class="chatlog__embed-content-container">
			<div class="chatlog__embed-content">
				<div class="chatlog__embed-text">
					<!-- @{/* Embed author */} -->
					{#if embed.author}
						<div class="chatlog__embed-author-container">
							<!-- TODO: check url -->
							{#if embed.author?.iconUrl?.url}
								<img class="chatlog__embed-author-icon" src="{checkUrl(embed.author?.iconUrl?.url)}" alt="Author icon" onerror="this.style.visibility='hidden'"
						width="{embed.author?.width ?? 16}"
						height="{embed.author?.height ?? 16}"
						>
							{/if}
							{#if embed.author.name}
								{#if embed.author.url}
									<a class="chatlog__embed-author-link" href="{embed.author.url}">
										<div class="chatlog__embed-author">{embed.author.name}</div>
									</a>
								{:else}
									<div class="chatlog__embed-author">{embed.author.name}</div>
								{/if}
							{/if}
						</div>
					{/if}

					<!-- @{/* Embed title */} -->
					{#if embed.title}
						<div class="chatlog__embed-title">
							{#if embed.url}
								<a class="chatlog__embed-title-link" href={embed?.url}>
									<div class="chatlog__markdown chatlog__markdown-preserve">
										<MessageMarkdown content={embed.title} />
									</div>
								</a>
							{:else}
								<div class="chatlog__markdown chatlog__markdown-preserve">
									<MessageMarkdown content={embed.title} />
								</div>
							{/if}
						</div>
					{/if}

					<!-- @{/* Embed description */} -->
					{#if embed.description}
						<div class="chatlog__embed-description">
							<div class="chatlog__markdown chatlog__markdown-preserve">
								<MessageMarkdown content={embed.description}/>
							</div>
						</div>
					{/if}

					<!-- @{/* Embed fields */} -->
					{#if embed.fields}
						<div class="chatlog__embed-fields">
							{#each embed.fields as field}
								<div class="chatlog__embed-field">
									{#if field.name}
										<div class="chatlog__embed-field-name">
											<div class="chatlog__markdown chatlog__markdown-preserve">
												<MessageMarkdown content={field.name} embed={true}/>
											</div>
										</div>
									{/if}

									{#if field.value}
										<div class="chatlog__embed-field-value">
											<div class="chatlog__markdown chatlog__markdown-preserve">
												<MessageMarkdown content={field.value} embed={true}/>
											</div>
										</div>
									{/if}
								</div>
							{/each}
						</div>
					{/if}


				<!-- @{/* Embed content */} -->
					{#if embed.thumbnail}
						<div class="chatlog__embed-thumbnail-container">
								<!-- {console.warn(embed.thumbnail.type)} -->
								{#if embed.thumbnail?.url?.type === 'video'}
									<a class="chatlog__embed-thumbnail-link" href="{embed.thumbnail?.url?.url}" target="_blank">
										<video class="chatlog__embed-thumbnail-video" src="{checkUrl(embed.thumbnail?.url?.url)}" autoplay loop muted playsinline
										width="{embed.thumbnail?.width ?? 16}"
										height="{embed.thumbnail?.height ?? 16}"/>
									</a>
								{:else if embed.thumbnail?.url?.url}
									<ImageGallery asset={embed.thumbnail} imgclass={"chatlog__embed-thumbnail"} />
								{/if}
						</div>
					{/if}

					<!-- @{/* Embed images */} -->
					{#if embed.images}
						{#each embed.images as image}
							<div class="chatlog__embed-images">
								<div class="chatlog__embed-image-container">
									<ImageGallery asset={image} imgclass={"chatlog__embed-image"} />
								</div>
							</div>
						{/each}
					{/if}

					<!-- @{/* Embed footer & icon */} -->
					{#if embed.footer}
						<div class="chatlog__embed-footer">
							{#if embed.footer.icon}
								<ImageGallery imgclass="chatlog__embed-footer-icon" inline={true} asset={embed.footer.icon} alt="Footer icon" onerror="this.style.visibility='hidden'" />
							{/if}

							<span class="chatlog__embed-footer-text">
							{#if embed.footer.text}
								{embed.footer.text}
								{#if embed.timestamp}
									{" • "} {embed.timestamp}
								{/if}
							{/if}
							</span>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/each}