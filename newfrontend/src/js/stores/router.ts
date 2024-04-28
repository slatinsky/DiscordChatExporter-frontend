// save state and restore it on back button push or page reload

import { get } from "svelte/store"
import { selectedChannelId, selectedGuildId, selectedThreadId } from "./guildStore"

function updateState() {
    let guildId = get(selectedGuildId)
    let channelId = get(selectedChannelId)
    let threadId = get(selectedThreadId)

    let state = {
        guild: guildId,
        channel: channelId,
        thread: threadId
    }

    // create an copy with non-null values
    let nonNullState = { }
    for (const key in state) {
        if (state[key] !== null) {
            nonNullState[key] = state[key]
        }
    }

    const searchParams = new URLSearchParams(nonNullState);
    const getParams = searchParams.toString()

    window.history.pushState(state, "", `/?${getParams}`)
    console.log("router - pushed state", state, getParams)
}

let timeout1: any = null
let timeout2: any = null
let restoringState = false
function restoreState(guildId, channelId, threadId) {
    // TODO: TEMPORARILY DISABLED
    return

    if (timeout1) {
        clearTimeout(timeout1)
    }
    if (timeout2) {
        clearTimeout(timeout2)
    }
    if (restoringState) {
        return
    }
    restoringState = true
    console.log("router - restoring state", guildId, channelId, threadId);

    selectedGuildId.set(guildId)
    timeout1 = setTimeout(() => {
        selectedChannelId.set(channelId)
    }, 500)
    timeout2 = setTimeout(() => {
        selectedThreadId.set(threadId)
    }, 1000)
    setTimeout(() => {
        restoringState = false
    }, 1200)
}

function restoreParamsFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    let guildId = urlParams.get("guild")
    let channelId = urlParams.get("channel")
    let threadId = urlParams.get("thread")

    restoreState(guildId, channelId, threadId)
    console.log("router - restored", window.location.search, urlParams, guildId, channelId, threadId)
}


export function initRouter() {
    // restore store on load
    restoreParamsFromUrl()

    selectedGuildId.subscribe((newGuildId) => {
        updateState()
    })
    selectedChannelId.subscribe((newChannelId) => {
        updateState()
    })
    selectedThreadId.subscribe((newThreadId) => {
        updateState()
    })

    // back button fires popstate
    window.addEventListener("popstate", (e) => {
        restoreState(e.state.guild, e.state.channel, e.state.thread)
    })
}