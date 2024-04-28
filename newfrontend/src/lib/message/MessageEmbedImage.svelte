<script lang="ts">
    import type { Asset } from "../../js/interfaces";
    import ImageGallery from "../ImageGallery.svelte"
    export let image: Asset
</script>

<div class="embed-image">
    <ImageGallery asset={image} imgclass={""} />
</div>