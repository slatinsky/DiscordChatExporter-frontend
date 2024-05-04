<script lang="ts">
    import { untrack } from "svelte";
    import type { Message } from "../js/interfaces";
    // --------------------------
    // THIS CODE IS NOT FINISHED
    // TODO: needs backend pagination support to optimize loading
    // --------------------------
    import { messsageIdsToMessages } from "../js/messages";
    import ChannelStart from "./message/ChannelStart.svelte";

    interface MyProps {
        ids: string[]
        guildId: string
        selectedMessageId: string | null
        isThread: boolean
        renderMessageSnippet: (message: Message, previousMessage: Message) => void
    }
    let { ids, guildId, selectedMessageId = null, isThread, renderMessageSnippet}: MyProps = $props();

    let maxMessages = 120
    let loadIncrement = 30
    let startLoadingPixels = 500
    let scrollContainer: HTMLDivElement

    let messages: Message[] = $state([])
    let lowestLoadedIndex: number | null = $state(null)
    let highestLoadedIndex: number | null = $state(null)
    let loadedIds: string[] = $state([])
    let watchScroll: boolean = $state(false)

    async function refetchMessages(loadedIds: string[]) {
        messages = await messsageIdsToMessages(guildId, loadedIds)
    }

    async function idsChanged() {
        console.log('scroller - ids changed - selectedMessageId', selectedMessageId, "ids length", ids.length)
        if (ids.length === 0) {
            console.log('scroller - no messages to load')
            messages = []
            return
        }
        watchScroll = false
        // let centerIndex = Math.round(ids.length / 2)

        let centerIndex
        if (selectedMessageId) {
            centerIndex = ids.indexOf(selectedMessageId)
            console.log('scroller - selected message index', centerIndex)
        }
        else {
            console.log('scroller - no selected message')
        }

        if (!centerIndex || centerIndex < 0) {
            centerIndex = Math.round(ids.length - 1)
        }

        highestLoadedIndex = centerIndex
        lowestLoadedIndex = centerIndex
        loadedIds = [ids[centerIndex]]
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
        setTimeout(async() => {
            if (!scrollContainer) {  // did we destroy the component before the timeout happened?
                return
            }

            // scroll to selected message
            if (selectedMessageId) {
                // find selected message index
                if (loadedIds.includes(selectedMessageId)) {
                    let selectedMessageElement = scrollContainer.querySelector(`[data-messageid="${selectedMessageId}"]`)
                    if (selectedMessageElement) {
                        selectedMessageElement.scrollIntoView({ block: "start", behavior: "instant" })
                        console.log('scroller - selected message scrolled into view')
                    }
                    else {
                        console.log('scroller - selected message not found in loaded messages')
                    }
                }
                else {
                    console.log('scroller - selected message not found in loaded messages', JSON.stringify(loadedIds), selectedMessageId)
                }
            }
            else {
                scrollContainer.scrollTop = scrollContainer.scrollHeight
                console.log('scroller - no selected message to scroll to')
            }
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


    // https://github.com/sveltejs/svelte/issues/9248#issuecomment-1732246774
    function explicitEffect(fn, depsFn) {
        $effect(() => {
            depsFn();
            untrack(fn);
        });
    }
    // run idsChanged() only if ids change
    explicitEffect(
        () => {
            idsChanged()
        },
        () => [ids]
    );

    async function handleScroll(event) {
        if (!watchScroll)
            return
        if (messages.length === 0)
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

<div class="scroll-container" onscroll={handleScroll} bind:this={scrollContainer}>
    {#if messages}
        {#each messages as message, index (message._id)}
            {#if index === 0}
                <ChannelStart channelName={message.channelName} isThread={isThread} />
            {/if}
            <div data-messageid={message._id}>
                {@render renderMessageSnippet(message, messages[index - 1])}
            </div>
        {/each}
    {/if}
</div>


<style>
    .scroll-container {
        height: 100%;
        overflow-y: auto;

        /* Needed for bottom aligment */
        /* can't use justify-content: flex-end, because that would break scroll */
        /* https://stackoverflow.com/a/37515194 */
        display: flex;
        flex-flow: column nowrap;
        padding-bottom: 32px;
        /* - */
    }

    /* align messages to the bottom if there are not enough messages to fill the container height */
    :global(.scroll-container > :first-child) {
        margin-top: auto !important;
    }
    /* - */

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