<script lang="ts">
    import MessageStickerLottie from "./MessageStickerLottie.svelte";
    import type { Sticker } from "../../js/interfaces";
    import Image from "../imagegallery/Image.svelte";

    export let stickers: Sticker[];
</script>

<div>
    {#each stickers as sticker}
        {#if sticker?.format === "Lottie"}
            <MessageStickerLottie asset={sticker.source} />
        {:else}
            <div class="image-sticker">
                <Image asset={sticker.source} />
            </div>
        {/if}
    {/each}
</div>

<style>
    .image-sticker {
        max-width: 200px;
        height: auto;
    }
</style>