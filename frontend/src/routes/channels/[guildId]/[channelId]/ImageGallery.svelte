<script>
	import { checkUrl, getFileNameFromUrl } from '../../../../helpers';
    export let url
    export let imgclass

    function viewGallery() {
        showGallery = true;
    }

    let showGallery = false;
</script>

<div class:media-spoiler={getFileNameFromUrl(url?.url).startsWith('SPOILER')}>
    <img
        on:click={viewGallery}
        class={imgclass}
        src={checkUrl(url?.url)}
        alt="Attachment"
        loading="lazy"
        width="{url.width ?? undefined}"
        height="{url.height ?? undefined}"
        onerror="this.style.visibility='hidden'"
    />
</div>

{#if showGallery}
    <div class="gallery-wrapper" on:click={()=>showGallery=false}>
        <div class="gallery-closebtn" on:click={()=>showGallery=false}>&times;</div>
        <div class="imgbox" on:click|stopPropagation>
            <img class="center-fit" src={checkUrl(url?.url)}>
            <div class="open-original">
                <a href={checkUrl(url?.url)} target="_blank">Open original</a>
            </div>
        </div>
    </div>
{/if}

<style>
    .chatlog__attachment img {
        cursor: pointer;
    }

    .gallery-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.8);
        z-index: 1000;
        display: flex;
        justify-content: center;
        align-items: center;

        display: flex;
        flex-direction: column;
        padding-top: .7rem;
    }

    .gallery-closebtn {
        position: absolute;
        top: -15px;
        right: 0;
        padding: 10px;
        color: white;
        cursor: pointer;

        font-size: 3rem;
        font-weight: 600;
    }

    .imgbox {
        display: grid;
        margin: .7rem;
        text-align: left;
    }
    .center-fit {
        max-width: 100%;
        max-height: calc(100vh - 60px);
        margin: auto;
    }

    .open-original {
        margin-bottom: .6rem;
        margin-top: .4rem;
    }
    .open-original > a {
        color: gray;
    }
</style>