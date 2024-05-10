import type { Asset } from "../../js/interfaces";

let isGalleryShown: boolean = $state(false);
let assets: Asset[] = $state([]);
let shownAssetIndex: number = $state(0);
let assetsCount: number = $derived(assets.length);
let shownAsset: Asset | null = $derived(assets.find((_, i) => i === shownAssetIndex) || null);


export function getImagegalleryState() {
    function showSingleAsset(newAsset: Asset) {
        assets = [newAsset];
        shownAssetIndex = 0;
        isGalleryShown = true;
        console.log("imagegallery - showSingleAsset", $state.snapshot(newAsset));
    }

    function showMultipleAssets(newAssets: Asset[], assetToShow: Asset) {
        assets = newAssets;
        shownAssetIndex = assets.findIndex((asset) => asset._id === assetToShow._id);
        isGalleryShown = true;

        console.log("imagegallery - showMultipleAssets", $state.snapshot(assets), $state.snapshot(shownAssetIndex));
    }


    function nextAsset() {
        shownAssetIndex = (shownAssetIndex + 1) % assets.length;
    }

    function previousAsset() {
        shownAssetIndex = (shownAssetIndex - 1 + assets.length) % assets.length;
    }

    function closeGallery() {
        isGalleryShown = false;
    }

    return {
        get isGalleryShown() {
            return isGalleryShown;
        },
        get shownAsset() {
            return shownAsset;
        },
        get assetsCount() {
            return assetsCount;
        },
        showSingleAsset,
        showMultipleAssets,
        closeGallery,
        nextAsset,
        previousAsset,
    };
}

