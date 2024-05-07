<script lang="ts">
    import { checkUrl } from '../../js/helpers';
    import IconGalleryUpArrow from '../icons/IconGalleryUpArrow.svelte';
    import { getImagegalleryState } from './imagegalleryState.svelte';

	const imagegalleryState = getImagegalleryState();
</script>

{#if imagegalleryState.isGalleryShown}
	<div class="gallery-wrapper" on:click={imagegalleryState.closeGallery}>
        {#if imagegalleryState.assetsCount > 1}
            <button class="prevbtn" on:click|stopPropagation={imagegalleryState.previousAsset}><IconGalleryUpArrow width={26} /></button>
            <button class="nextbtn" on:click|stopPropagation={imagegalleryState.nextAsset}><IconGalleryUpArrow width={26} /></button>
        {/if}
		<button class="closebtn" on:click={imagegalleryState.closeGallery}>&times;</button>
		<div class="imgbox" on:click|stopPropagation>
			<img src={checkUrl(imagegalleryState.shownAsset)} width={imagegalleryState.shownAsset?.width ?? undefined} height={imagegalleryState.shownAsset?.height ?? undefined}>
			<div class="open-original">
				<a href={checkUrl(imagegalleryState.shownAsset)} target="_blank">Open in Browser</a>
			</div>
		</div>
	</div>
{/if}


<style>
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

        .closebtn {
            position: absolute;
            top: -15px;
            right: 0;
            padding: 10px;
            color: white;
            cursor: pointer;

            font-size: 3rem;
            font-weight: 600;
        }

        .prevbtn,
        .nextbtn {
            position: absolute;
            top: 50%;
            color: #9d9d9d;
            cursor: pointer;

            width: 50px;
            height: 50px;

            display: grid;
            place-items: center;
        }

        .prevbtn:hover,
        .nextbtn:hover {
            color: white;
        }

        .prevbtn {
            left: 10px;
            transform: rotate(270deg);
        }

        .nextbtn {
            right: 10px;
            transform: rotate(90deg);
        }

        .imgbox {
            display: grid;
            margin: .7rem;
            text-align: left;

            /* Make SVGs larger in the gallery */
            img[src$=".svg"] {
                width: 100%;
                height: 100%;
            }

            img {
                width: 100%;
                height: 100%;
                max-width: 100%;
                max-height: calc(100vh - 40px);
                margin: auto;
            }

            .open-original {
                margin-bottom: .6rem;
                margin-top: .2rem;

                & > a {
                    color: #878788;
                    font-size: 14px;
                    text-decoration: none;
                    font-weight: 500;
                }
                & > a:hover {
                    text-decoration: underline;
                }
            }
        }
    }
</style>