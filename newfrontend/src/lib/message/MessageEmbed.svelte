<script lang="ts">
    import { checkUrl } from "../../js/helpers";
    import type { Embed } from "../../js/interfaces";
    import IconPlayerPlay from "../icons/IconPlayerPlay.svelte";
    import IconOpenLink from "../icons/IconOpenLink.svelte";
    import IconPoop from "../icons/IconPoop.svelte";
    import MessageMarkdown from "./MessageMarkdown.svelte";
    import { renderTimestamp } from "../../js/time";
    import MessageTiledImages from "./MessageTiledImages.svelte";

    interface MyProps {
        embed: Embed;
    }
    let { embed }: MyProps = $props();

    let playingVideo: boolean = $state(false)

    let authorIconFailedToLoad: boolean = $state(false)
    let thumbnailFailedToLoad: boolean = $state(false)
    let footerIconFailedToLoad: boolean = $state(false)

    const spotifyRegex = /https:\/\/open\.spotify\.com\/track\/([a-zA-Z0-9]+)/
    let spotifyMatch = $derived(embed.url?.match(spotifyRegex))
    let spotifyId = $derived(spotifyMatch ? spotifyMatch[1] : null)

    const youtubeRegex = /^(?:https?:)?\/\/(?:www|m)\.(?:youtube(?:-nocookie)?\.com|youtu.be)\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?[\w\-]+/
	let youtubeId = $derived(embed.url?.match(youtubeRegex)?.[0]?.split('v=')?.[1]?.split('&')?.[0] ?? null);

    const twitchClipRegex = /(?:https:\/\/)?clips\.twitch\.tv\/(\S+)/i
    let twitchClipMatch = $derived(embed.url?.match(twitchClipRegex))
    let twitchClipId = $derived(twitchClipMatch ? twitchClipMatch[1] : null)

    let smallThumbnail: boolean = $derived.by(() => {
        if (spotifyId) {
            return false
        }

        if (embed.hasOwnProperty('video')) {
            return false
        }

        return true
    })

    function playVideo() {
        playingVideo = true
    }

    function onAuthorIconError(e: Event) {
        console.log('author icon error', e)
        authorIconFailedToLoad = true
    }

    function onThumbnailError(e: Event) {
        console.log('thumbnail error', e)
        thumbnailFailedToLoad = true
    }

    function onFooterIconError(e: Event) {
        console.log('footer icon error', e)
        footerIconFailedToLoad = true
    }
</script>

<div class="main-wrapper">
    {#if spotifyId}
        <iframe src={`https://open.spotify.com/embed/track/${spotifyId}`} frameborder="0" sandbox="allow-forms allow-modals allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts" style="width: 400px; height: 80px;"></iframe>
    {:else if embed.video && embed.title === "" && embed.description === ""}
        <video class="embed-video" controls preload="metadata" style="aspect-ratio: {embed.video.width} / {embed.video.height}">
            <source src={checkUrl(embed.video)}>
        </video>
    {:else}
        <div class="embed" class:smallthumbnail={smallThumbnail} style="border-left: {embed.color} 4px solid;">
            <div class="header-row">
                <div class="header-col">
                    {#if youtubeId}
                        <div class="website-name">YouTube</div>
                    {:else if twitchClipId}
                        <div class="website-name">Twitch</div>
                    {/if}
                    {#if embed.author}
                        <div class="author-name">
                            {#if embed.author.icon && !authorIconFailedToLoad}
                                <img class="author-icon" src={checkUrl(embed.author.icon)} alt="" width="24" height="24" onerror={onAuthorIconError} />
                            {/if}
                            <a href={embed.author.url} target="_blank" rel="noopener noreferrer">{embed.author.name}</a>
                        </div>
                    {/if}

                    <div class="title">
                        {#if embed.url}
                            <a href={embed.url} target="_blank" rel="noopener noreferrer">{embed.title}</a>
                        {:else}
                            {embed.title}
                        {/if}
                    </div>

                    {#if !twitchClipId}
                        <div class="description">
                            <MessageMarkdown content={embed.description} />
                        </div>
                    {/if}
                </div>

                {#if embed.thumbnail && !playingVideo}
                    <div class="thumb-col">
                        <div class="thumbnail-wrapper">
                            {#if thumbnailFailedToLoad}
                                <IconPoop width={smallThumbnail ? 80 : 200} />
                            {:else}
                                <img src={checkUrl(embed.thumbnail)} alt="" onerror={onThumbnailError} />
                                <div class="pill">
                                    <button class="icon" onclick={playVideo}>
                                        <IconPlayerPlay width={24} />
                                    </button>
                                    <a class="icon" href={embed.url} target="_blank" rel="noopener noreferrer">
                                        <IconOpenLink width={24} />
                                    </a>
                                </div>
                            {/if}
                        </div>
                    </div>
                {/if}

                {#if playingVideo}
                    <iframe
                        class="twitch-iframe"
                        allow="autoplay" frameborder="0" scrolling="no" sandbox="allow-forms allow-modals allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts" provider="Twitch"
                        src="https://clips.twitch.tv/embed?clip={twitchClipId}&parent={window.location.hostname}"
                        width="400" height="232" allowfullscreen="">
                    </iframe>
                {/if}
            </div>

            {#if embed.fields.length > 0}
                <div class="fields">
                    {#each embed.fields as field}
                        <div class="field">
                            <div class="field-name">{field.name}</div>
                            <div class="field-value"><MessageMarkdown content={field.value} /></div>
                        </div>
                    {/each}
                </div>
            {/if}

            {#if embed.images.length > 0}
                <div class="image-embeds-wrapper">
                    <MessageTiledImages images={embed.images} isAttachment={false} />
                </div>
            {/if}


            {#if embed.footer}
                <div class="footer">
                    <div class="footer-row">
                        {#if embed.footer.icon && !footerIconFailedToLoad}
                            <img class="footer-icon" src={checkUrl(embed.footer.icon)} alt="" width="20" height="20" onerror={onFooterIconError} />
                        {/if}
                        <span class="footer-text">{embed.footer?.text}</span><span class="footer-separator">•</span><span class="footer-timestamp">{renderTimestamp(embed.timestamp)}</span>
                    </div>
                </div>
            {/if}
        </div>
    {/if}
</div>

<style>
    .main-wrapper {
        padding: 2px 0;

        .embed-video {
            width: 100%;
            max-width: 400px;
            height: auto;
            border-radius: 3px;
        }
    }

    .embed {
        background-color: #2B2D31;
        border-radius: 4px;
        padding: 8px 16px 16px 12px;
        max-width: 432px;

        &.smallthumbnail .header-row {
            display: flex;

            .thumb-col {
                .thumbnail-wrapper {
                    margin: 8px 0 0 16px;
                }
            }
        }

        .header-row .header-col {
            flex: 1;

            .website-name {
                margin-top: 8px;
                font-weight: 400;
                font-size: 12px;
                color: #b6bac1;
            }

            .author-name {
                margin-top: 8px;
                font-weight: 600;
                font-size: 14px;

                display: flex;
                align-items: center;

                .author-icon {
                    margin-right: 8px;
                }

                a {
                    color: #f2f3f5;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            }

            .title {
                margin-top: 8px;
                font-size: 16px;
                font-weight: 600;

                a {
                    color: #53a8f9;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            }

            .description {
                font-size: 14px;
                font-weight: 400;
                line-height: 18px !important;
                margin-top: 8px;
            }
        }


        .thumb-col {
            display: grid;
            place-items: center;

            .thumbnail-wrapper {
                position: relative;
                margin-top: 16px;
                width: 100%;
                max-width: 400px;


                img {
                    width: 100%;
                    border-radius: 3px;
                }

                .pill {
                    position: absolute;

                    display: flex;
                    justify-content: space-between;
                    gap: 3px;

                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);

                    width: 54px;
                    height: 24px;
                    padding: 12px;
                    border-radius: 24px;

                    box-sizing: content-box;


                    background-color: rgba(0, 0, 0, 0.6);
                    .icon {
                        opacity: .6;
                        cursor: pointer;
                        display: block;
                        color: white;
                    }
                    .icon:hover {
                        opacity: 1;
                    }
                }
            }
        }

        .twitch-iframe {
            margin-top: 16px;
            width: 100%;
            border-radius: 3px;
            max-width: 400px;
            max-height: 232px;
        }

        .fields {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 8px;
            margin-top: 8px;

            .field {
                width: calc(33.33% - 8px);
                .field-name {
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 2px;
                    color: #f2f3f5;
                }

                .field-value {
                    font-size: 14px;
                    font-weight: 400;
                    color: #dcdee1;
                    width: 100%;
                }
            }
        }

        .image-embeds-wrapper {
            margin-top: 16px;
        }


        .footer {
            margin-top: 8px;
            .footer-row {
                font-size: 12px;
                font-weight: 500;
                color: #dcdee1;
                display: flex;
                align-items: center;

                .footer-icon {
                    margin-right: 8px;
                }

                .footer-separator {
                    margin: 0 4px
                }
            }
        }
    }
</style>