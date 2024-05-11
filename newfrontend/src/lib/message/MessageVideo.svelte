<script lang="ts">
    import { checkUrl } from "../../js/helpers";
    import type { Asset } from "../../js/interfaces";

    interface MyProps {
        attachment: Asset;
    }
    let { attachment }: MyProps = $props();
</script>

<div class:media-spoiler={attachment.filenameWithoutHash.startsWith('SPOILER')}>
    <video class="message-video" controls preload="metadata" style="aspect-ratio: {attachment.width} / {attachment.height}">
        <source src={checkUrl(attachment)} title="Video: {attachment.filenameWithoutHash} ({Math.round(attachment.sizeBytes / 1024)} KB)">
    </video>
</div>


<style>
    .message-video {
        max-width: 80%;
        max-height: 500px;
        vertical-align: top;
        border-radius: 3px;
        object-position:left;
        width: auto;
        height: auto;

        &:fullscreen {
            object-position:center;
        }
    }
</style>