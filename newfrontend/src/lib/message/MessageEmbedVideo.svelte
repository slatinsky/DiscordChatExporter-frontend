<script lang="ts">
    import { checkUrl } from "../../js/helpers";
    import { gifs, online } from "../../js/stores/settingsStore.svelte";

    export let embed


    const regTenor = /^^(?:https?:)?\/\/(?:www\.)?(?:tenor\.com)\/(?:view|watch)\/[%\w\-]+-(\d+)/
    $: embedUrl = embed?.url ?? null;
    $: tenorId = embedUrl?.match(regTenor)?.[1] ?? null;

</script>

{#if tenorId && embed.hasOwnProperty('video')}
    <!-- render video gifs locally, video field was added in DCE 2.42.3 -->
    <video class="message-videogif" src="{checkUrl(embed.video)}" autoplay loop muted playsinline/>
{:else if embed.hasOwnProperty('video')}
    <!-- render ordinary embeded video -->
    <video class="message-video" controls preload="metadata">
        <source src={checkUrl(embed.video)}>
    </video>
{:else if tenorId && $online && $gifs && !embed.hasOwnProperty('video')}
    <!-- workaround for older exports (embed tenor iframe) -->
    <div class="embed-tenor-container" style="aspect-ratio: {embed.thumbnail?.width ?? 1} / {embed.thumbnail?.height ?? 1};">
        <iframe class="embed-tenor" src="https://tenor.com/embed/{tenorId}" frameBorder="0" allowfullscreen style="aspect-ratio: {embed.thumbnail?.width ?? 1} / {embed.thumbnail?.height ?? 1};"></iframe>
    </div>
{/if}


<style>
    .embed-tenor-container {
		pointer-events: none;
	}
	.embed-tenor-container, .embed-tenor {
		width: 300px;
		height: auto;
		max-width: 100%;
		max-height: 100%;
	}

    .message-videogif {
		max-width: 80%;
		max-height: 500px;
		vertical-align: top;
		border-radius: 3px;
		object-position:left;
		width: auto;
		height: auto;
	}
</style>