import type { Asset } from "../../js/interfaces";

let isGalleryShown: boolean = $state(false);
let assets: Asset[] = $state([]);
let shownAssetIndex: number = $state(0);
let assetsCount: number = $derived(assets.length);
let shownAsset: Asset | null = $state(null);

export function getImagegalleryState() {

    function _updateShownAsset() {
        shownAsset = assets.find((_, i) => i === shownAssetIndex) || null;
    }

    function showSingleAsset(newAsset: Asset) {
        if (!newAsset) {
            console.error("imagegallery - showSingleAsset: newAsset is empty");
            return;
        }
        showMultipleAssets([newAsset], newAsset);
    }

    function showMultipleAssets(newAssets: Asset[], assetToShow: Asset) {
        if (!newAssets.length) {
            console.error("imagegallery - showMultipleAssets: newAssets is empty");
            return;
        }
        if (!assetToShow) {
            console.error("imagegallery - showMultipleAssets: assetToShow is empty");
            return;
        }
        assets = newAssets;
        shownAssetIndex = assets.findIndex((asset) => asset._id === assetToShow._id);
        _updateShownAsset();
        isGalleryShown = true;

        console.log("imagegallery - showMultipleAssets", $state.snapshot(assets), $state.snapshot(shownAssetIndex));
    }


    function nextAsset() {
        shownAssetIndex = (shownAssetIndex + 1) % assets.length;
        _updateShownAsset();
    }

    function previousAsset() {
        shownAssetIndex = (shownAssetIndex - 1 + assets.length) % assets.length;
        _updateShownAsset();
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

