<script lang="ts">
	import type { Asset } from 'src/js/interfaces';
	import { checkUrl } from '../../../../js/helpers';
	export let asset: Asset

	export let imgclass: string = '';

	export let inline = false;
	export let alt: string = '';
	export let width: number | undefined = undefined;
	export let height: number | undefined = undefined;

	let domImg: HTMLImageElement;

	function viewGallery() {
		// if doesn't have class media-spoiler, then show gallery
		if (!domImg.classList.contains('media-spoiler')) {
			showGallery = true;
		}
	}

	let showGallery = false;

	$: isSpoiler = asset?.filenameWithoutHash.startsWith('SPOILER');
</script>



<img
	bind:this={domImg}
	class:media-spoiler={isSpoiler} 
	on:click={viewGallery}
	class="inline {imgclass}"
	src={checkUrl(asset)}
	alt="Attachment"
	width="{asset?.width ?? undefined}"
	height="{asset?.height ?? undefined}"
	onerror="this.style.visibility='hidden'"
/>


{#if showGallery}
	<div class="gallery-wrapper" on:click={()=>showGallery=false}>
		<div class="gallery-closebtn" on:click={()=>showGallery=false}>&times;</div>
		<div class="imgbox" on:click|stopPropagation>
			<img class="center-fit" src={checkUrl(asset)} {alt} {width} {height}>
			<div class="open-original">
				<a href={checkUrl(asset)} target="_blank">Open original</a>
			</div>
		</div>
	</div>
{/if}
<style>
    .chatlog__attachment img {
        cursor: pointer;
    }

    .gallery-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.8);
        z-index: 1020;
        display: flex;
        justify-content: center;
        align-items: center;

        display: flex;
        flex-direction: column;
        padding-top: .7rem;
    }

    .gallery-closebtn {
        position: absolute;
        top: -15px;
        right: 0;
        padding: 10px;
        color: white;
        cursor: pointer;

        font-size: 3rem;
        font-weight: 600;
    }

    .imgbox {
        display: grid;
        margin: .7rem;
        text-align: left;
    }

    /*Make SVGs larger in the gallery*/
    .imgbox img[src$=".svg"] {
        width: 100%;
        height: 100%;
    }

    .center-fit {
        max-width: 100%;
        max-height: calc(100vh - 60px);
        margin: auto;
    }

    .open-original {
        margin-bottom: .6rem;
        margin-top: .4rem;
    }
    .open-original > a {
        color: gray;
    }

	.inline {
		display: inline-block;
        cursor: pointer;
	}
</style>