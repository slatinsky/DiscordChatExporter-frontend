<script lang="ts">

	import { onMount } from "svelte";
    import lottie from "lottie-web";
    import { checkUrl } from "../../js/helpers";
    import type { Asset } from "../../js/interfaces";

    export let asset: Asset;
    let element: HTMLElement;

    onMount(async () => {
        lottie.loadAnimation({
            container: element,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            path: checkUrl(asset)
        });
    });
</script>

<div class="lottie" bind:this={element}></div>

<style>
    .lottie {
        width: 160px;
        height: 160px;
    }
</style>