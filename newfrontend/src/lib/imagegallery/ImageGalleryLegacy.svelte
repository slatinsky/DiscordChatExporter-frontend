<script lang="ts">
    import { checkUrl } from '../../js/helpers';
    import type { Asset } from '../../js/interfaces';
    import { getImagegalleryState } from './imagegalleryState.svelte';
    interface MyProps {
        asset: Asset;
        imgclass: string;
        imgstyle: string | undefined;
        inline: boolean;
        alt: string;
        width: string | undefined;
        height: string | undefined;
    }
    let { asset, imgclass = '', imgstyle = '', inline = false, alt = '', width = undefined, height = undefined}: MyProps = $props();

	let domImg: HTMLImageElement;

	function viewGallery() {
		// if doesn't have class media-spoiler, then show gallery
		if (!domImg.classList.contains('media-spoiler')) {
			showGallery = true;
		}
	}

	let showGallery = $state(false);

	let isSpoiler = $derived(asset?.filenameWithoutHash.startsWith('SPOILER'));

    const imagegalleryState = getImagegalleryState();
</script>



<img
	bind:this={domImg}
	class:media-spoiler={isSpoiler}
	on:click={()=>imagegalleryState.showSingleAsset(asset)}
	class="inline {imgclass}"
	src={checkUrl(asset)}
	alt="Attachment"
    style={imgstyle}
	width="{width ?? asset?.width ?? undefined}"
	height="{height ?? asset?.height ?? undefined}"
/>
