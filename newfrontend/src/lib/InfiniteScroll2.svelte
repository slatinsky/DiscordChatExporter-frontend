<script lang="ts">
    import { onMount, tick, type Snippet } from "svelte";
    import { messsageIdsToMessages } from "../js/messages";

    interface MyProps {
        fetchMessageIds: (direction: "before" | "after" | "around" , messageId: string, limit: number) => Promise<string[]>
        guildId: string
        snippetMessage: Snippet
    }

    let { fetchMessageIds, guildId, snippetMessage}: MyProps = $props();

    let SHOWDEBUG = true

    // message id can be 24 length strings or be "first" or "last"
    let ids = $state<string[]>([])
    let renderedIds = $state<string[]>([])
    let messages = $state<any[]>([])
    let topReached = $derived(renderedIds.includes("first"))
    let bottomReached = $derived(renderedIds.includes("last"))
    let earliestRenderedId = $state<string | null>(null)
    // const renderedCount = 50

    let scrollContainerHeight = $state(1000)
    let scrollableHeight = $state(2000)
    let maxRenderedCount = $derived(Math.max(100, Math.ceil(scrollContainerHeight / 10)))
    let marginPixels = $derived((scrollableHeight - scrollContainerHeight) / 8)

    async function fetchIdsBefore(messageId: string) {
        const newMessageIds = await fetchMessageIds("before", messageId, maxRenderedCount)
        return [...newMessageIds, ...ids]
    }

    async function fetchIdsAfter(messageId: string) {
        const newMessageIds = await fetchMessageIds("after", messageId, maxRenderedCount)
        return [...ids, ...newMessageIds]
    }

    async function fetchIdsAround(messageId: string) {
        const newMessageIds = await fetchMessageIds("around", messageId, maxRenderedCount)
        return newMessageIds
    }


    function calculateRenderedIdsAround(messageId: string) {
        if (!ids.includes(messageId)) {
            console.warn(`messageId ${messageId} not found in ids`)
            return
        }

        const countToRender = Math.min(maxRenderedCount, ids.length)
        let suggestedToRender = [messageId]
        let renderedCount = 1
        for (let i = 1; i < countToRender; i++) {
            const before = ids[ids.indexOf(messageId) - i]
            const after = ids[ids.indexOf(messageId) + i]
            if (before) {
                suggestedToRender.unshift(before)
                renderedCount++
            }
            if (after) {
                suggestedToRender.push(after)
                renderedCount++
            }
            if (renderedCount >= countToRender) {
                break
            }
        }

        return suggestedToRender
    }

    let watchScroll = $state(true)
    async function handleScroll(event) {
        scrollableHeight = event.target.scrollHeight
        if (ids.length === 0) {
            return
        }
        if (!watchScroll) {
            return
        }

        const element = event.target
        const scrollTop = element.scrollTop
        const scrollBottom = element.scrollHeight - element.clientHeight - scrollTop

        if (!topReached && scrollTop < marginPixels) {
            watchScroll = false
            // save position of first rendered message
            const id = renderedIds[0]
            const firstRenderedMessage = element.querySelector(`[data-messageid="${id}"]`)

            // let position
            // if (firstRenderedMessage) {
            //     position = firstRenderedMessage.getBoundingClientRect()
            // }
            // else {
            //     console.warn(`firstRenderedMessage ${id} not found`)
            // }


            if (ids[0] === renderedIds[0]) {  // if not cached
                const newIds = await fetchIdsBefore(ids[0])
                ids = newIds
            }

            renderedIds = calculateRenderedIdsAround(id)
            messages = await messsageIdsToMessages(guildId, renderedIds)
            // renderedIds = newIds
            await tick();  // wait for render

            // restore scroll position
            // if (position) {
            //     const newFirstRenderedMessage = element.querySelector(`[data-messageid="${id}"]`)
            //     if (newFirstRenderedMessage) {
            //         const newPosition = newFirstRenderedMessage.getBoundingClientRect()
            //         element.scrollTop = newPosition.top - position.top + scrollTop
            //     }
            //     else {
            //         console.warn(`newFirstRenderedMessage ${id} not found`)
            //     }
            // }

            watchScroll = true
        }
        else if (!bottomReached && scrollBottom < marginPixels) {
            watchScroll = false
            const id = renderedIds[renderedIds.length - 1]

            if (ids[ids.length - 1] === renderedIds[renderedIds.length - 1]) {  // if not cached
                const newIds = await fetchIdsAfter(ids[ids.length - 1])
                ids = newIds
            }
            renderedIds = calculateRenderedIdsAround(id)
            messages = await messsageIdsToMessages(guildId, renderedIds)
            // renderedIds = newIds
            await tick();  // wait for render
            watchScroll = true
        }
    }

    let scrollContainer: HTMLDivElement
    onMount(async () => {
        const newMessageIds = await fetchMessageIds("around", "last", maxRenderedCount)
        ids = newMessageIds
        renderedIds = calculateRenderedIdsAround("last")
        messages = await messsageIdsToMessages(guildId, renderedIds)
        await tick();
        // const tout = setTimeout(async() => {
            if (scrollContainer) {
                scrollContainer.scrollTop = scrollContainer.scrollHeight
                console.log("scrolling to bottom")
            }
            else {
                console.warn("scrollContainer not found") 
            }
        // }, 0)


        // const inter1 = setInterval(() => {
        //     if (scrollContainer) {
        //         const scrollTop = scrollContainer.scrollTop
        //         if (!topReached && scrollTop < 10) {
        //             scrollContainer.scrollTop = 150
        //             console.log("fixing scroll position")
        //             return
        //         }
        //     }
        // }, 1000)

        // return () => {
        //     clearInterval(inter1)
        // }

        // return () => {
        //     clearTimeout(tout)
        // }
    })
</script>


<div class="wrapper">
    {#if SHOWDEBUG}
        <small class="debug-container">rendered {renderedIds.length} / {ids.length}, topReached {topReached} ({renderedIds[0]}), bottomReached {bottomReached} ({renderedIds[renderedIds.length - 1]}), container height {scrollContainerHeight}px, maxRenderedCount {maxRenderedCount}, scrollableHeight {scrollableHeight}px, marginPixels {marginPixels}px</small>
    {/if}
    <div class="scroll-container" onscroll={handleScroll} bind:this={scrollContainer} bind:clientHeight={scrollContainerHeight}>
        {#each messages as message (message._id)}
            <div class="message" data-messageid={message._id}>
                <!-- <div>{message._id}</div> -->
                {@render snippetMessage(message, message)}
            </div>
        {/each}
    </div>
</div>

<style>
    .wrapper {
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .message {
        min-height: 30px;
    }
    .scroll-container {
        flex: 1;
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