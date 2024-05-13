<script lang="ts">
    import { checkUrl } from "../../js/helpers";
    import type { Asset } from "../../js/interfaces";

    interface MyProps {
        attachment: Asset;
    }
    let { attachment }: MyProps = $props();
</script>

<div class="spoiler-wrapper">
    <div class="" class:media-spoiler={attachment.filenameWithoutHash.startsWith('SPOILER')}>
        <video class="message-video" controls preload="metadata" style="aspect-ratio: {attachment.width} / {attachment.height}">
            <source src={checkUrl(attachment)} title="Video: {attachment.filenameWithoutHash} ({Math.round(attachment.sizeBytes / 1024)} KB)">
        </video>
    </div>
</div>


<style>
    .message-video {
        vertical-align: top;
        width: auto;
        height: auto;
    }

    .spoiler-wrapper {
        overflow: hidden;
        border-radius: 3px;
        width: fit-content;
        max-width: 550px;
    }
</style>