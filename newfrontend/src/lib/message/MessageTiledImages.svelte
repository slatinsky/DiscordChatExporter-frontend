<script lang="ts">
    import { checkUrl } from '../../js/helpers';
    import type { Asset } from '../../js/interfaces';
    import { getImagegalleryState } from '../imagegallery/imagegalleryState.svelte';

    interface MyProps {
        images: Asset[];
    }
    let { images }: MyProps = $props();

	const imagegalleryState = getImagegalleryState();
    let groupedImageAttachments = $derived.by(() => {
		if (images.length == 0) {
			return [];
		}

		let rows = [];
		if (images.length == 1) {
			rows.push([images[0]]);
		}
		else if (images.length == 2) {
			rows.push([images[0], images[1]]);
		}
		else if (images.length == 3) {
			rows.push([images[0]]);
			rows.push([images[1], images[2]]);
		}
		else if (images.length == 4) {
			rows.push([images[0], images[1]]);
			rows.push([images[2], images[3]]);
		}
		else if (images.length == 5) {
			rows.push([images[0], images[1]]);
			rows.push([images[2], images[3], images[4]]);
		}
		else if (images.length % 3 == 0) {
			for (let i = 0; i < images.length; i += 3) {
				rows.push([images[i], images[i + 1], images[i + 2]]);
			}
		}
		else if (images.length % 3 == 1) {
			rows.push([images[0]]);
			for (let i = 1; i < images.length; i += 3) {
				rows.push([images[i], images[i + 1], images[i + 2]]);
			}
		}
		else if (images.length % 3 == 2) {
			rows.push([images[0], images[1]]);
			for (let i = 2; i < images.length; i += 3) {
				rows.push([images[i], images[i + 1], images[i + 2]]);
			}
		}
		return rows;
	});
</script>

{#snippet imageSnippet(allImages, image, aspectRatio)}
    <img
        class:setaspectratio={aspectRatio}
        on:click={()=>imagegalleryState.showMultipleAssets(allImages, image)}
        src={checkUrl(image)}
        alt={image.caption}
        width={image?.width ?? undefined}
        height={image?.height ?? undefined}
    />
{/snippet}

<div class="images" class:images3={images.length == 3}>
    {#each groupedImageAttachments as imageGroup}
        <div class="image-row" >
            {#each imageGroup as image}
                {@render imageSnippet(images, image, imageGroup.length > 1 || images.length == 3)}
            {/each}
        </div>
    {/each}
</div>


<style>
    .images {
        border-radius: 8px;
        .image-row {
            display: grid;
            grid-auto-columns: minmax(0, 1fr);
            grid-auto-flow: column;
            width: 100%;
            gap: 4px;
            margin-bottom: 4px;
        }
    }

    img {
        object-fit: cover;
        width: 100%;
        height: auto;
        border-radius: 3px;
    }

    img.setaspectratio {
        aspect-ratio: 1 / 1;
    }

    /*
    3 image layout is special - flip the layout:

    +---+ +---+
    | 1 | | 2 |          +---------++---+
    +---+ +---+          |         || 1 |
    +---------+     ➤   |    3    |+---+
    |         |          |         |+---+
    |    3    |          |         || 2 |
    |         |          +---------++---+
    |         |
    +---------+
    */
    .images.images3 {
        display: flex;
        gap: 4px;
        max-width: 550px;

        .image-row {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .image-row:nth-child(1) {
            width: 66.7%;
        }
        .image-row:nth-child(2) {
            width: 33%;
        }
    }
</style>