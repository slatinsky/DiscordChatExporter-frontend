<script lang="ts">
    import { checkUrl } from '../../js/helpers';
    import type { Asset } from '../../js/interfaces';
    import { getImagegalleryState } from './imagegalleryState.svelte';
    interface MyProps {
        assets?: Asset[] | null;
        asset: Asset;
		inline?: boolean;
		class?: string;
		alt?: string;
		clickable?: boolean;
		forceSpoiler?: boolean | null;
		onerror?: (event: Event) => void;
    }
    let { assets = null, asset, inline = false, class: divclass = "", alt = "", clickable = true, forceSpoiler = null, onerror = undefined, ...otherProps}: MyProps = $props();
	let manualSpoilerHidden = $state(false)
	let isBlurred = $derived.by(()=> {
		if (manualSpoilerHidden) {
			return false
		}
		if (forceSpoiler !== null) {
			return forceSpoiler
		}
		if (asset?.filenameWithoutHash.startsWith('SPOILER')) {
			return true
		}
		return false
	});

	function viewGallery() {
		if (isBlurred) {
			manualSpoilerHidden = true
		}
		else {
			if (assets) {
				imagegalleryState.showMultipleAssets(assets, asset)
			}
			else {
				imagegalleryState.showSingleAsset(asset)
			}
		}
	}
    const imagegalleryState = getImagegalleryState();
</script>


<div class="spoiler-wrapper {divclass}" onclick={clickable ? viewGallery : undefined} class:clickable={clickable}>
	<img
		class:media-spoiler={isBlurred}
		src={checkUrl(asset)}
		width="{asset?.width ?? undefined}"
		height="{asset?.height ?? undefined}"
		{alt}
		{...otherProps}
		onerror={onerror}
	/>
</div>


<style>
	.clickable {
		cursor: pointer;
	}
	.spoiler-wrapper {
		overflow: hidden;
		img.media-spoiler {
			filter: blur(100px);
			cursor: pointer;
		}

		img {
			width: 100%;
			height: 100%;
			object-fit: cover;
		}
	}

</style>