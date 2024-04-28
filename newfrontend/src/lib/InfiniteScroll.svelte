<script lang="ts">
    // --------------------------
    // THIS CODE IS NOT FINISHED
    // TODO: needs backend pagination support to optimize loading
    // --------------------------
    import { messsageIdsToMessages } from "../js/messages";

    export let ids
    export let guildId

    let scrollContainer: HTMLDivElement
    let messages = []
    let maxMessages = 120
    let loadIncrement = 30
    let startLoadingPixels = 500
    let lowestLoadedIndex = null
    let highestLoadedIndex = null
    let loadedIds: string[] = []
    let watchScroll = false

    async function refetchMessages(loadedIds) {
        messages = await messsageIdsToMessages(guildId, loadedIds)
    }

    async function idsChanged(ids) {
        watchScroll = false
        // let centerIndex = Math.round(ids.length / 2)
        let centerIndex = Math.round(ids.length - 1)
        highestLoadedIndex = centerIndex
        lowestLoadedIndex = centerIndex
        loadedIds = []
        for (let i = 1; i < maxMessages; i++) { // TODO: rewrite using slice
            if (centerIndex + i < ids.length) {
                highestLoadedIndex = centerIndex + i
                loadedIds = [...loadedIds, ids[highestLoadedIndex]]
            }
            if (centerIndex - i >= 0) {
                lowestLoadedIndex = centerIndex - i
                loadedIds = [ids[lowestLoadedIndex], ...loadedIds, ]
            }
        }

        await refetchMessages(loadedIds)
        setTimeout(() => {
            // scrollContainer.scrollTop = scrollContainer.scrollHeight / 2
            scrollContainer.scrollTop = scrollContainer.scrollHeight
        watchScroll = true
        }, 0)
    }

    async function loadLowUnloadHigh() {
        for (let i = 1; i < loadIncrement; i++) { // TODO: rewrite using slice
            if (lowestLoadedIndex - 1 >= 0) {
                // add lowest
                lowestLoadedIndex = lowestLoadedIndex - 1
                loadedIds = [ids[lowestLoadedIndex], ...loadedIds]

                // remove highest
                if (loadedIds.length > maxMessages) {
                    highestLoadedIndex = highestLoadedIndex - 1
                    loadedIds = loadedIds.slice(0, -1)
                }
            }
            else {
                console.log('scroller - top of the page - No more messages to load.')
                break
            }
        }

        await refetchMessages(loadedIds)
        watchScroll = true

    }

    async function loadHighUnloadLow() {
        for (let i = 1; i < loadIncrement; i++) { // TODO: rewrite using slice
            if (highestLoadedIndex + 1 < ids.length) {
                // add highest
                highestLoadedIndex = highestLoadedIndex + 1
                loadedIds = [...loadedIds, ids[highestLoadedIndex]]

                // remove lowest
                if (loadedIds.length > maxMessages) {
                    lowestLoadedIndex = lowestLoadedIndex + 1
                    loadedIds = loadedIds.slice(1)
                }
            }
            else {
                console.log('scroller - bottom of the page - No more messages to load.')
                break
            }
        }

        await refetchMessages(loadedIds)
        watchScroll = true
    }

    $: idsChanged(ids)





    async function handleScroll(event) {
        if (!watchScroll)
            return

        const element = event.target
        let margin = startLoadingPixels
        if (element.scrollTop < margin) {
            watchScroll = false
            console.log('scroller - reached top of the page')
            loadLowUnloadHigh()
        }
        if (element.scrollHeight - element.scrollTop <= element.clientHeight + margin) {
            watchScroll = false
            console.log('scroller - reached bottom of the page')
            loadHighUnloadLow()
        }
    }
</script>

<div class="scroll-container" on:scroll={handleScroll} bind:this={scrollContainer}>
    {#if messages}
        {#each messages as message (message._id)}
            <slot name="item" message={message} />
        {/each}
    {/if}
</div>


<style>
    .scroll-container {
        height: 100%;
        overflow-y: auto;
    }

    .scroll-container::-webkit-scrollbar-track {
        background-color: #2b2d31;
    }
    .scroll-container::-webkit-scrollbar-corner {
        background-color: #646464;
    }

    .scroll-container::-webkit-resizer {
        background-color: #666;
    }
    .scroll-container::-webkit-scrollbar-track-piece {
        background-color:#313338;
    }
    .scroll-container::-webkit-scrollbar {
    height: 3px;
        width: 14px;
    }
    .scroll-container::-webkit-scrollbar-thumb {
        height: 50px;
        background-color: #1a1b1e;

        width: 5px;
        border-radius: 10px;

        /*left+right scrollbar padding magix*/
        background-clip: padding-box;
        border: 3px solid rgba(0, 0, 0, 0);
    }
</style>