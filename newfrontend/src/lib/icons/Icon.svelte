<script lang="ts">
    import playerPause from "./player/pause.svg?raw"
    import playerPlay from "./player/play.svg?raw"
    import playerRestart from "./player/restart.svg?raw"
    import playerVolumeHigh from "./player/volumeHigh.svg?raw"
    import playerVolumeLow from "./player/volumeLow.svg?raw"
    import playerVolumeMuted from "./player/volumeMuted.svg?raw"
    import openLink from "./player/openLink.svg?raw"
    import filetypeArchive from "./filetype/archive.svg?raw"
    import filetypeAudio from "./filetype/audio.svg?raw"
    import filetypeDocument from "./filetype/document.svg?raw"
    import filetypePdf from "./filetype/pdf.svg?raw"
    import filetypeSpreadsheet from "./filetype/spreadsheet.svg?raw"
    import filetypeUnknown from "./filetype/unknown.svg?raw"
    import dcefEmpty from "./dcef/empty.svg?raw"
    import dcefFilled from "./dcef/filled.svg?raw"
    import replyAttachment from "./reply/attachment.svg?raw"
    import replyDeleted from "./reply/deleted.svg?raw"
    import systemMessageBoost from "./systemmessage/boost.svg?raw"
    import systemMessageJoin from "./systemmessage/join.svg?raw"
    import systemMessageLeave from "./systemmessage/leave.svg?raw"
    import systemMessageEdit from "./systemmessage/edit.svg?raw"
    import call from "./systemmessage/call.svg?raw"
    import pinned from "./systemmessage/pinned.svg?raw"
    import channel from "./channeltype/channel.svg?raw"
    import channelWithThreads from "./channeltype/channelWithThreads.svg?raw"
    import news from "./channeltype/news.svg?raw"
    import voice from "./channeltype/voice.svg?raw"
    import thread from "./channeltype/thread.svg?raw"
    import poop from "./placeholder/poop.svg?raw"
    import noPins from "./placeholder/no-pins.svg?raw"
    import noSearchResults from "./placeholder/no-search-results.svg?raw"

    import download from "./other/download.svg?raw"
    import dropdown from "./other/dropdown.svg?raw"
    import hamburger from "./other/hamburger.svg?raw"
    import settings from "./other/settings.svg?raw"
    import shield from "./other/shield.svg?raw"
    import verified from "./other/verified.svg?raw"
    import magnifyingGlass from "./other/magnifying-glass.svg?raw"
    import help from "./other/help.svg?raw"
    import bin from "./other/bin.svg?raw"
    import plus from "./other/plus.svg?raw"

    import arrowUp from "./modal/arrowUp.svg?raw"
    import modalX from "./modal/x.svg?raw"

    type IconOptions =  "player/pause" |
                        "player/play" |
                        "player/restart" |
                        "player/volumeHigh" |
                        "player/volumeLow" |
                        "player/volumeMuted" |
                        "player/openLink" |
                        "filetype/archive" |
                        "filetype/audio" |
                        "filetype/document" |
                        "filetype/pdf" |
                        "filetype/spreadsheet" |
                        "filetype/unknown" |
                        "dcef/empty" |
                        "dcef/filled" |
                        "reply/attachment" |
                        "reply/deleted" |
                        "systemmessage/boost" |
                        "systemmessage/join" |
                        "systemmessage/leave" |
                        "systemmessage/edit" |
                        "systemmessage/call" |
                        "systemmessage/pinned" |
                        "channeltype/channel" |
                        "channeltype/channelWithThreads" |
                        "channeltype/news" |
                        "channeltype/voice" |
                        "channeltype/thread" |
                        "placeholder/poop" |
                        "placeholder/no-pins" |
                        "placeholder/no-search-results" |
                        "other/download" |
                        "other/dropdown" |
                        "other/hamburger" |
                        "other/settings" |
                        "other/shield" |
                        "other/verified" |
                        "other/magnifying-glass" |
                        "other/help" |
                        "other/bin" |
                        "other/plus" |
                        "modal/arrowUp" |
                        "modal/x"

	interface MyProps {
        name: IconOptions;
        width: number;
        height?: number;
    }
    let { name, width, height: inputHeight, inline=false }: MyProps = $props();
    let height = $derived(inputHeight ? inputHeight : width);
</script>

<div class="icon" class:inline={inline} style="width: {width}px; height: {height}px;">
    {#if name === "player/play"}
        {@html playerPlay}
    {:else if name === "player/pause"}
        {@html playerPause}
    {:else if name === "player/restart"}
        {@html playerRestart}
    {:else if name === "player/volumeHigh"}
        {@html playerVolumeHigh}
    {:else if name === "player/volumeLow"}
        {@html playerVolumeLow}
    {:else if name === "player/volumeMuted"}
        {@html playerVolumeMuted}
    {:else if name === "player/openLink"}
        {@html openLink}
    {:else if name === "filetype/archive"}
        {@html filetypeArchive}
    {:else if name === "filetype/audio"}
        {@html filetypeAudio}
    {:else if name === "filetype/document"}
        {@html filetypeDocument}
    {:else if name === "filetype/pdf"}
        {@html filetypePdf}
    {:else if name === "filetype/spreadsheet"}
        {@html filetypeSpreadsheet}
    {:else if name === "filetype/unknown"}
        {@html filetypeUnknown}
    {:else if name === "dcef/empty"}
        {@html dcefEmpty}
    {:else if name === "dcef/filled"}
        {@html dcefFilled}
    {:else if name === "reply/attachment"}
        {@html replyAttachment}
    {:else if name === "reply/deleted"}
        {@html replyDeleted}
    {:else if name === "systemmessage/boost"}
        {@html systemMessageBoost}
    {:else if name === "systemmessage/join"}
        {@html systemMessageJoin}
    {:else if name === "systemmessage/leave"}
        {@html systemMessageLeave}
    {:else if name === "systemmessage/edit"}
        {@html systemMessageEdit}
    {:else if name === "systemmessage/call"}
        {@html call}
    {:else if name === "systemmessage/pinned"}
        {@html pinned}
    {:else if name === "channeltype/channel"}
        {@html channel}
    {:else if name === "channeltype/channelWithThreads"}
        {@html channelWithThreads}
    {:else if name === "channeltype/news"}
        {@html news}
    {:else if name === "channeltype/voice"}
        {@html voice}
    {:else if name === "channeltype/thread"}
        {@html thread}
    {:else if name === "placeholder/poop"}
        {@html poop}
    {:else if name === "placeholder/no-pins"}
        {@html noPins}
    {:else if name === "placeholder/no-search-results"}
        {@html noSearchResults}
    {:else if name === "other/download"}
        {@html download}
    {:else if name === "other/dropdown"}
        {@html dropdown}
    {:else if name === "other/hamburger"}
        {@html hamburger}
    {:else if name === "other/settings"}
        {@html settings}
    {:else if name === "other/shield"}
        {@html shield}
    {:else if name === "other/verified"}
        {@html verified}
    {:else if name === "other/magnifying-glass"}
        {@html magnifyingGlass}
    {:else if name === "other/help"}
        {@html help}
    {:else if name === "other/bin"}
        {@html bin}
    {:else if name === "other/plus"}
        {@html plus}
    {:else if name === "modal/arrowUp"}
        {@html arrowUp}
    {:else if name === "modal/x"}
        {@html modalX}
    {:else}
        <div>Icon "{name}" not found</div>
    {/if}
</div>

<style>
    .icon {
        display: grid;
        place-items: center;
    }

    .icon > :global(svg) {
        width: 100%;
        height: 100%;
    }
</style>