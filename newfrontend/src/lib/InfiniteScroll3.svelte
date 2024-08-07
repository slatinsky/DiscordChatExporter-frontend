<script lang="ts">
    import { onMount, tick, type Snippet } from "svelte";
    import {throttle, debounce} from 'lodash-es';

    interface MyProps {
        fetchMessages: (direction: "before" | "after" | "around" , messageId: string, limit: number) => Promise<string[]>
        guildId: string
        snippetMessage: Snippet
        scrollToMessageId: string
    }

    let { fetchMessages, guildId, snippetMessage, scrollToMessageId}: MyProps = $props();

    let SHOWDEBUG = false
    let scrollContainer: HTMLDivElement
    let messages = $state<any[]>([])
    let prevPage = $state<string | null>(null)
    let nextPage = $state<string | null>(null)
    let loadIsThrottled = false
    let scrollDisabled = $state(true)

    const MSGCOUNT_INITIAL = 50
    const MSGCOUNT_MORE = 20



    async function handleScroll(event: Event) {

        if (loadIsThrottled) {
            console.log('loadf throttled')
            debouncedHandleScroll(event)
            event.preventDefault()
            return
        }
        if (scrollDisabled) {
            event.preventDefault()
            return
        }
        console.log('scrolling', prevPage, nextPage)
        // if at the top of scroll container, load more messages before
        if (prevPage && scrollContainer.scrollTop === 0) {
            console.log('top reached')
            loadIsThrottled = true
            scrollDisabled = true
            const bottomOffset = scrollContainer.scrollHeight - scrollContainer.clientHeight
            const moreMessages = await fetchMessages("before", prevPage, MSGCOUNT_MORE)
            console.log('moreMessages', moreMessages)
            messages = [...moreMessages.messages, ...messages]
            prevPage = moreMessages.prevPage
            await tick();  // wait for render

            // restore the same bottom offset
            let newScrollTop = scrollContainer.scrollHeight - scrollContainer.clientHeight - bottomOffset
            scrollContainer.scrollTop = newScrollTop
            scrollDisabled = false
            loadIsThrottled = false
        }
        // if at the bottom of scroll container, load more messages after
        if (nextPage && scrollContainer.scrollTop + scrollContainer.clientHeight >= scrollContainer.scrollHeight - 1) {
            console.log('bottom reached')
            loadIsThrottled = true
            scrollDisabled = true
            const moreMessages = await fetchMessages("after", nextPage, MSGCOUNT_MORE)
            console.log('moreMessages', moreMessages)
            messages = [...messages, ...moreMessages.messages]
            nextPage = moreMessages.nextPage
            scrollDisabled = false
            loadIsThrottled = false
        }
    }
    // debounce handleScroll
    const debouncedHandleScroll = debounce(handleScroll, 250)

    function scrollToMessageIdF(messageId: string) {
        if (!scrollContainer) {
            return
        }
        if (messageId === "last") {
            scrollContainer.scrollTop = scrollContainer.scrollHeight
            return
        }
        const messageElement = scrollContainer.querySelector(`[data-messageid="${messageId}"]`)
        if (messageElement) {
            messageElement.scrollIntoView({ behavior: "smooth", block: "center" })
        }
    }

    onMount(async () => {
        console.log('onMount')
        const newMessages = await fetchMessages("around", scrollToMessageId, MSGCOUNT_INITIAL)
        console.log('newMessages', newMessages)
        messages = newMessages.messages
        prevPage = newMessages.prevPage
        nextPage = newMessages.nextPage
        await tick();  // wait for render
        scrollToMessageIdF(scrollToMessageId)
        setTimeout(() => {
            scrollToMessageIdF(scrollToMessageId)
        }, 200)
        setTimeout(() => {
            scrollToMessageIdF(scrollToMessageId)
            scrollDisabled = false
        }, 500)

    })
</script>


<div class="wrapper">
    {#if SHOWDEBUG}
        <small class="debug-container">scrollToMessageId {scrollToMessageId}</small>
    {/if}
    <div class="scroll-container" onscroll={handleScroll} bind:this={scrollContainer}>
        {#each messages as message (message._id)}
            <div class="message" data-messageid={message._id}>
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