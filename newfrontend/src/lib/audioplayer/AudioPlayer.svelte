<script lang="ts">
    import { fade } from 'svelte/transition';
    import { getAudioplayerState } from './audioplayerState.svelte';
    import Icon from '../icons/Icon.svelte';

	interface MyProps {
        src: string;
    }
    let { src }: MyProps = $props();

    const audioplayerState = getAudioplayerState();

    let audio: HTMLAudioElement;
    let paused: boolean = $state(true);
    let duration: number = $state(0);
    let muted: boolean = $state(false);

    let currentTime: number = $state(0);
    let bufferedTime: number = $state(0);
    let tooltip: HTMLDivElement;
    let tooltipX: number = $state(0);
    let seekText: string = $state("");
    let seekingMedia: boolean = $state(false);
    let seekingVolume: boolean = $state(false);
    let mediaProgress: HTMLDivElement;
    let volumeBar: HTMLDivElement;
    let ended: boolean = $derived(currentTime >= duration);

    let mouseOverMediaBar: boolean = $state(false);
    let showTooltip: boolean = $derived(mouseOverMediaBar || seekingMedia);
    let showMediaHandle: boolean = $derived(mouseOverMediaBar || seekingMedia);

    let mouseOverVolumeIcon: boolean = $state(false);
    let mouseOverVolumeBar: boolean = $state(false);
    let showVolume: boolean = $derived(mouseOverVolumeIcon || mouseOverVolumeBar || seekingVolume);


    function calculateSeekX(event: MouseEvent, bounds: DOMRect): number {
        let x = event.pageX - bounds.left;
        return Math.min(Math.max(x / bounds.width, 0), 1);
    }
    function calculateSeekY(event: MouseEvent, bounds: DOMRect): number {
        let y = bounds.height - (event.pageY - bounds.top);
        return Math.min(Math.max(y / bounds.height, 0), 1);
    }

    function seekMedia(event: MouseEvent) {
        audio.currentTime = calculateSeekX(event, mediaProgress.getBoundingClientRect()) * duration;
    }

    function seekVolume(event: MouseEvent) {
        if (!volumeBar) return;
        audioplayerState.setVolume(calculateSeekY(event, volumeBar.getBoundingClientRect()));
        muted = false;
    }

    function formatTime(seconds: number) {
        if (!seconds && seconds !== 0) {
            return "--:--";
        }

        const display_seconds = Math.floor(seconds % 60);
        const display_minutes = Math.floor(seconds / 60 % 60);
        const display_hours = Math.floor(seconds / 3600);

        if (display_hours > 0) {
            return `${display_hours}:${display_minutes.toString().padStart(2, "0")}:${display_seconds.toString().padStart(2, "0")}`;
        } else {
            return `${display_minutes}:${display_seconds.toString().padStart(2, "0")}`;
        }
    }

    function seekTooltip(event: MouseEvent) {
        let mediaProgressBounds = mediaProgress.getBoundingClientRect();
        let tooltipBounds = tooltip.getBoundingClientRect();
        let tooltipWidth = tooltipBounds.width;
        tooltipX = event.pageX - mediaProgressBounds.x - tooltipWidth / 2;
        tooltipX = Math.min(Math.max(tooltipX, -tooltipWidth / 2), mediaProgressBounds.width - tooltipWidth / 2);
        let seekValue = (event.pageX - mediaProgressBounds.left) * duration / mediaProgressBounds.width;
        seekValue = Math.min(Math.max(seekValue, 0), duration);
        seekText = formatTime(seekValue);
    }

    function trackMouse(event: MouseEvent) {
        if (seekingMedia) {
            seekMedia(event)
        }
        if (showTooltip) {
            seekTooltip(event)
        }
        if (seekingVolume) {
            seekVolume(event);
        }
    }

    function handlePlayPause() {
        if (audio.paused) {
            audio.play();
            muted = false;
        } else {
            audio.pause();
        }
    }

    function handleMouseUp() {
        seekingMedia = false
        seekingVolume = false;
    }


    function handlePlay() {
        paused = false;
    }
    function handlePause() {
        paused = true;
    }

    function updateBuffered() {
        if (audio.readyState > 0) {
            bufferedTime =  audio.buffered.end(audio.buffered.length - 1)
        }
        else {
            bufferedTime = 0;
        }
    }
</script>

<svelte:window
    onmouseup={handleMouseUp}
    onmousemove={trackMouse}
/>

<div class="audioplayer" style="--buffered-width: {bufferedTime / duration * 100}%; --playing-width: {currentTime / duration * 100}%;--volume-height: {muted ? 0 : audioplayerState.volume * 100}%;--volumehandle-height: {muted ? 0 : audioplayerState.volume * 90}%;">
    <button
        class="icon handlePlayPause-btn"
        onclick={handlePlayPause}>
        {#if ended}
            <Icon name="player/restart" width={24} />
        {:else if paused}
            <Icon name="player/play" width={24} />
        {:else}
            <Icon name="player/pause" width={24} />
        {/if}
    </button>
    <div class="time">
        <div class="current-time">{formatTime(currentTime)}</div>
        <div>/</div>
        <div class="duration">{formatTime(duration)}</div>
    </div>
    <div class="tooltip-wrapper">
        <div
            transition:fade={{duration: 100}}
            bind:this={tooltip}
            class="tooltip" class:hide={!showTooltip}
            style="left: {tooltipX}px;">
            {#if showTooltip}
                {seekText}
            {:else}
                {#if duration > 3600}
                    --:--:--
                {:else}
                    --:--
                {/if}
            {/if}
        </div>
    </div>
    <div
        class="mediaprogress-wrapper"
        bind:this={mediaProgress}
        value={currentTime ? currentTime : 0}
        max={duration}
        style=""
        onmousedown={() => seekingMedia = true}
        onmouseenter={() => mouseOverMediaBar = true}
        onmouseleave={() => mouseOverMediaBar = false}
        onclick={seekMedia}
    >
        <div class="inner">
            <div class="buffer"></div>
            <div class="progress"></div>
            <div class="handle" class:hidden={!showMediaHandle}></div>
        </div>
    </div>
    <button
        class="icon"
        onclick={() => muted = !muted}
        onmouseenter={() => mouseOverVolumeIcon = true}
        onmouseleave={() => mouseOverVolumeIcon = false}
    >
        {#if muted || audioplayerState.volume < .01}
            <Icon name="player/volumeMuted" width={24} />
        {:else if audioplayerState.volume < .5}
            <Icon name="player/volumeLow" width={24} />
        {:else}
            <Icon name="player/volumeHigh" width={24} />
        {/if}
    </button>
    <div
        bind:this={volumeBar}
        class="volumeprogress-wrapper"
        class:hide={!showVolume}
        onmousedown={() => seekingVolume = true}
        onclick={seekVolume}
        onmouseenter={() => mouseOverVolumeBar = true}
        onmouseleave={() => mouseOverVolumeBar = false}
    >
        <div class="inner">
            <div class="progress"></div>
            <div class="handle"></div>
        </div>
    </div>
</div>

<audio
	bind:this={audio}
	bind:duration
    bind:currentTime
    muted={muted || seekingMedia}
    bind:volume={audioplayerState.volume}
	onplay={handlePlay}
    onpause={handlePause}
    ontimeupdate={updateBuffered}
    onloadedmetadata={updateBuffered}
	{src}
	preload="metadata"
></audio>



<style>
    .audioplayer {
        /* colors */
        --background-color: #0C0D0E;
        --icon-color: #A0A0A1;
        --icon-color-hover:white;
        --text-color: white;
        --seek-full-color: #5865F2;
        --seek-buffered-color: #7F8082;
        --seek-unbuffered-color: #47494C;
        --seek-handle-color: #4752C4;

        --volume-full-color: #5865F2;
        --volume-empty-color: #45474A;
        --volume-handle-color: #4752C4;
        /* - */

        border-radius: 3px;

        display: flex;
        flex-direction: row;
        align-items: center;
        background-color: var(--background-color);
        padding: 0 5px;
        user-select: none;
        position: relative;
    }

    .tooltip-wrapper {
        position: relative;
        font-size: 12px;
        font-weight: 600;

        .tooltip {
            bottom: 15px;
            position: absolute;
            background-color: var(--background-color);
            padding: 1px 7px;
            border-radius: 5px;
            color: var(--text-color);
            pointer-events: none;
            text-align: center;
        }

        .tooltip.hide {
            display: none;
        }
    }

    .icon {
        color: var(--icon-color);
        cursor: pointer;
        display: grid;
        place-items: center;
        height: 32px;

        &.handlePlayPause-btn {
            margin-right: 15px;
        }
    }
    .icon:hover {
        color: var(--icon-color-hover);
    }

    .time {
        display: flex;
        gap: 3px;
        margin-right: 5px;
        font-size: 12px;
        font-family: 'gg mono', monospace;
        font-weight: 500;
        color: var(--text-color);
    }


    .mediaprogress-wrapper {
        width: 100%;
        height: 32px;
        display: flex;
        align-items: center;
        margin-right: 8px;
        margin-left: 5px;

        & > .inner {
            position: relative;
            width: 100%;
            height: 6px;
            background-color: var(--seek-unbuffered-color);
            border-radius: 3px;

            & > .buffer,
            & > .progress {
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                border-radius: 3px;
            }

            & > .buffer {
                width: var(--buffered-width);
                background-color: var(--seek-buffered-color);
            }

            & > .progress {
                width: var(--playing-width);
                background-color: var(--seek-full-color);
            }

            & > .handle {
                position: absolute;
                top: -2px;
                left: calc(var(--playing-width) - 5px);
                width: 10px;
                height: 10px;
                background-color: var(--seek-handle-color);
                border-radius: 50%;

                &.hidden {
                    display: none;
                }
            }
        }
    }

    .volumeprogress-wrapper {
        position: absolute;
        width:50px;
        height: 100px;
        bottom: 32px;
        right: -8px;

        display: grid;
        place-items: center;

        &.hide {
            display: none;
        }

        & > .inner {
            position: relative;
            width: 6px;
            height: 100%;
            background-color: var(--volume-empty-color);
            border-radius: 12px;

            border: 5px solid #000000;
            box-sizing: content-box;

            & > .progress {
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: var(--volume-height);
                background-color: var(--volume-full-color);
                border-radius: 3px;
                /* transition: height 0.1s; */
            }

            & > .handle {
                position: absolute;
                bottom: calc(var(--volumehandle-height));
                left: -2px;
                width: 10px;
                height: 10px;
                background-color: var(--volume-handle-color);
                border-radius: 50%;
                display: none;
                /* transition: bottom 0.1s; */
            }
        }
    }
    .volumeprogress-wrapper:hover > .inner > .handle {
        display: block;
    }
</style>