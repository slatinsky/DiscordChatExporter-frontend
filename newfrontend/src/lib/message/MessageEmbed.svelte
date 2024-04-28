<script lang="ts">
    import MessageEmbedVideo from "./MessageEmbedVideo.svelte";
    import MessageEmbedImage from "./MessageEmbedImage.svelte";
    import { checkUrl } from "../../js/helpers";
    import ImageGallery from "../ImageGallery.svelte";
    import type { Embed } from "../../js/interfaces";

    export let embed: Embed

    let playVideo = false
</script>

<div class="embed">
    <pre>{JSON.stringify(embed, null, 2)}</pre>

    <MessageEmbedVideo embed={embed}/>

    {#if embed.thumbnail && !playVideo}
        <div>
                {#if embed.thumbnail?.type === 'video'}
                    <a href="{embed.thumbnail?.url}" target="_blank">
                        <video class="message-video" src="{checkUrl(embed.thumbnail)}" autoplay loop muted playsinline
                        width="{embed.thumbnail?.width}"
                        height="{embed.thumbnail?.height}"/>
                    </a>
                <!-- unknown because embed can be extensionless and image is the most common thumbnail -->
                {:else if embed.thumbnail?.type === 'image' || embed.thumbnail?.type === 'unknown'}
                    <ImageGallery asset={embed.thumbnail} imgclass={"message-thumbnail"} />
                {/if}
        </div>
    {/if}

    {#each embed.images as image}
        <MessageEmbedImage image={image}/>
    {/each}
</div>



<style>
    :global(.message-thumbnail) {
		flex: 0;
		max-width: calc(100% - 40px);
		max-height: 100%;
		max-height: auto;
		height: auto;
		margin-top: 1rem;
		margin-left: 1.2rem;
		border-radius: 3px
	}

    /* :global(.message-image), */
	/* :global(.message-videogif), */
	:global(.message-video) {
		max-width: 80%;
		max-height: 500px;
		vertical-align: top;
		border-radius: 3px;
		object-position:left;
		width: auto;
		height: auto;
	}
</style>