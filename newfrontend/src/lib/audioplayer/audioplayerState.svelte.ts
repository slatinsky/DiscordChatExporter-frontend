export function getAudioplayerState() {
    let volume = $state(1);      // each audio player has its own volume, we persist only the last set volume
    function setVolume(newVolume: number) {
        volume = newVolume;
        localStorage.setItem("audiovolume", volume.toString());
    }

    const savedVolume = localStorage.getItem("audiovolume");
    if (savedVolume) {
        volume = parseFloat(savedVolume);
    }

    return {
        get volume() {
            return volume;
        },
        set volume(newVolume: number) {  // required for bind:volume
            console.debug("setting volume ignored, use audioplayerState.setVolume instead (required for bind:volume)");
        },
        setVolume
    };
}

