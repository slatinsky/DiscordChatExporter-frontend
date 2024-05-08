<script lang="ts">
    import MessageStickerLottie from "./MessageStickerLottie.svelte";
    import type { Sticker } from "../../js/interfaces";
    import Image from "../imagegallery/Image.svelte";

    export let stickers: Sticker[];
</script>

<div class="chatlog__reactions">
    {#each stickers as sticker}
        {#if sticker?.format === "Lottie"}
            <MessageStickerLottie asset={sticker.source} />
        {:else}
            <div class="chatlog__sticker">
                <Image asset={sticker.source} class="chatlog__sticker-image" />
            </div>
        {/if}
    {/each}
</div>

<style>
    :global(.chatlog__sticker-image) {
        max-width: 200px;
        height: auto;
    }
</style>