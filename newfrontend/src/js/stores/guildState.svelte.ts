import { getSearchState } from "../../lib/search/searchState.svelte";
import { isObjectEqual } from "../helpers";
import { fetchCategoriesChannelsThreads, fetchGuilds, fetchMessageIds, fetchPinnedMessageIds } from "./api";
import { getLayoutState } from "./layoutState.svelte";

let guilds = $state(await fetchGuilds());
let guildId = $state("nonExistingGuildId");  // will be changed before the first load
let guild = $derived(guilds.find(g => g._id === guildId) || null);

let channelId = $state(null);
let categories = $state([]);
let channel = $derived(categories.flatMap(c => c.channels).find(c => c._id === channelId) || null);
let channelMessageId = $state(null);
let channelMessagesIds = $state([]);
let channelPinnedMessagesIds = $state([]);

let threadId = $state(null);
let thread = $derived(categories.flatMap(c => c.channels).flatMap(c => c.threads).find(t => t._id === threadId) || null);
let threadMessageId = $state(null);
let threadMessagesIds = $state([]);
let threadPinnedMessagesIds = $state([]);

// fast lookups:
// key is channelId, value is channel object
let channelsLookup = $derived.by(() => categories.flatMap(c => c.channels).reduce((acc, channel) => {
	acc[channel._id] = channel
	return acc
}, {}));

// key is threadId, value is thread object
let threadsLookup = $derived.by(() => categories.flatMap(c => c.channels).flatMap(c => c.threads).reduce((acc, thread) => {
	acc[thread._id] = thread
	return acc
}, {}));


export function isChannel(channelId: string) {
	return channelsLookup[channelId] !== undefined
}
export function isThread(threadId: string) {
	return threadsLookup[threadId] !== undefined
}

export function findChannel(channelId: string) {
	return channelsLookup[channelId]
}

export function findThread(threadId: string) {
	return threadsLookup[threadId]
}

export function findChannelThread(channelOrThreadId: string) {
	if (isChannel(channelOrThreadId)) {
		return findChannel(channelOrThreadId)
	}
	else if (isThread(channelOrThreadId)) {
		return findThread(channelOrThreadId)
	}
	else {
		console.warn("findChannelThread - channel or thread not found", channelOrThreadId)
		return null
	}
}

export function findChannelsByName(channelOrThreadName: string) {
	const lowerCaseName = channelOrThreadName.toLowerCase()
	const foundChannels = categories.flatMap(c => c.channels).filter(c => c.name.toLowerCase().includes(lowerCaseName))
	return foundChannels
}

export function findThreadsByName(channelOrThreadName: string) {
	const lowerCaseName = channelOrThreadName.toLowerCase()
	const foundThreads = categories.flatMap(c => c.channels).flatMap(c => c.threads).filter(t => t.name.toLowerCase().includes(lowerCaseName))
	return foundThreads
}

export function getGuildState() {
	function _getStateObject() {
		return {
			guild: guildId || null,
			channel: channelId || null,
			thread: threadId || null,
			channelmessage: channelMessageId || null,
			threadmessage: threadMessageId || null,
			search: searchState.submittedSearchPrompt || null
		}
	}

	function getUrlState() {
		const urlParams = new URLSearchParams(window.location.search)
		let state = {
			guild: urlParams.get("guild") || null,
			channel: urlParams.get("channel") || null,
			thread: urlParams.get("thread") || null,
			channelmessage: urlParams.get("channelmessage") || null,
			threadmessage: urlParams.get("threadmessage") || null,
			search: urlParams.get("search") || null
		}

		// convert null strings to null values
		for (const key in state) {
			if (state[key] === "null") {
				state[key] = null
			}
			if (state[key] === "undefined") {
				delete state[key]
			}
		}
		return state
	}

	/**
	 * Convert the state object to a query string
	 */
	function stateToParams(state) {
		let nonNullState: any = {}  // pretty url without null values
		for (const key in state) {
			if (state[key] !== null && state[key] !== undefined) {
				nonNullState[key] = state[key]
			}
		}
		const searchParams = new URLSearchParams(nonNullState);
		const getParams = searchParams.toString()
		return getParams
	}

	/**
	 * Pushes the current state to the browser history if it has changed
	 */
	async function pushState() {
		let state: any = _getStateObject()
		let previousState = window.history.state
		if (isObjectEqual(state, previousState)) {
			console.log("router - no changes detected")
			return
		}
		const getParams = stateToParams(state)
		window.history.pushState(state, `${state.guildId} ${state.channelId}`, `/?${getParams}`)
		console.log("router - pushed", state);
	}

	/**
	 * Replaces the current state in the browser history
	 * Call this after initial app load to set the initial state
	 */
	async function replaceState() {
		const state: any = _getStateObject()
		const getParams = stateToParams(state)
		window.history.replaceState(state, "", `/?${getParams}`)
		console.log("router - replaced", state);
	}

	async function changeGuildId(newGuildId: string | null) {
		if (newGuildId === "000000000000000000000000") {
			newGuildId = null
		}
		if (guildId === newGuildId) {
			return;
		}
		guildId = newGuildId;
		searchState.clearSearch()
		await changeChannelId(null)
		categories = await fetchCategoriesChannelsThreads(guildId)
		console.log("router - changed guildId", guildId);
	}

	async function changeChannelId(newChannelId: string | null) {
		if (channelId === newChannelId) {
			return;
		}
		channelId = newChannelId;
		await changeThreadId(null)

		if (newChannelId) {
			channelMessagesIds = await fetchMessageIds(guildId, newChannelId)
			channelMessageId = channelMessagesIds.length > 0 ? channelMessagesIds[-1] : null  // last message
			channelPinnedMessagesIds = await fetchPinnedMessageIds(guildId, newChannelId)
		}
		else {
			channelMessagesIds = []
			channelMessageId = null
			channelPinnedMessagesIds = []
		}
		console.log("router - changed channelId", channelId);
	}

	async function changeThreadId(newThreadId: string | null) {
		if (threadId === newThreadId) {
			return;
		}
		threadId = newThreadId;
		if (newThreadId && guildId) {
			threadMessagesIds = await fetchMessageIds(guildId, newThreadId)
			threadMessageId = threadMessagesIds.length > 0 ? threadMessagesIds[-1] : null  // last message
			threadPinnedMessagesIds = await fetchPinnedMessageIds(guildId, newThreadId)

			layoutState.showThread()
		}
		else {
			threadMessagesIds = []
			threadMessageId = null
			threadPinnedMessagesIds = []

			layoutState.hideThread()
		}
		console.log("router - changed threadId", threadId);
	}

	async function changeChannelMessageId(newMessageId: string | null) {
		let proposedChange
		if (newMessageId === null) {
			proposedChange = null
		}
		else if (channelMessagesIds.includes(newMessageId)) {
			proposedChange = newMessageId
		}
		else {
			console.error("router - changeChannelMessageId - message not found", newMessageId)
			proposedChange = null
		}

		if (proposedChange !== channelMessageId) {
			channelMessageId = proposedChange
			console.log("router - changed channelMessageId", channelMessageId);
		}
	}

	async function changeThreadMessageId(newMessageId: string | null) {
		let proposedChange
		if (newMessageId === null) {
			proposedChange = null
		}
		else if (threadMessagesIds.includes(newMessageId)) {
			proposedChange = newMessageId
		}
		else {
			console.error("router - changeThreadMessageId - message not found", newMessageId)
			proposedChange = null
		}

		if (proposedChange !== threadMessageId) {
			threadMessageId = proposedChange
			console.log("router - changed threadMessageId", threadMessageId);
		}
	}

	/**
	 * Switch to guildId and channelOrThreadId (will be automatically detected if it's a channel or thread id)
	 * Call pushState() after calling this to add new state to the history
	 */
	async function comboSetGuildChannel(guildId: string, channelOrThreadId: string) {
        await changeGuildId(guildId)
        if (isChannel(channelOrThreadId)) {
          await changeChannelId(channelOrThreadId)
        }
        else if (isThread(channelOrThreadId)) {
          await changeThreadId(channelOrThreadId)
        }
		else {
		  console.warn("router - comboSetGuildChannel - channel or thread not exported", channelOrThreadId)
		}
    }
	/**
	 * Same as above, but also sets the message id (in the channel if it's a channel, in the thread if it's a thread)
	 */
	async function comboSetGuildChannelMessage(guildId: string, channelOrThreadId: string, messageId: string) {
        await changeGuildId(guildId)
        if (isChannel(channelOrThreadId)) {
          await changeChannelId(channelOrThreadId)
          await changeChannelMessageId(messageId)
        }
        else if (isThread(channelOrThreadId)) {
          await changeThreadId(channelOrThreadId)
          await changeThreadMessageId(messageId)
        }
		else {
		  console.warn("router - comboSetGuildChannelMessage - channel or thread not exported", channelOrThreadId)
		}
    }

	return {
		get guildId() {
			return guildId;
		},
		get guilds() {
			return guilds;
		},
		get guild() {
			return guild;
		},
		get channelId() {
			return channelId;
		},
		get categories() {
			return categories;
		},
		get channel() {
			return channel;
		},
		get threadId() {
			return threadId;
		},
		get thread() {
			return thread;
		},
		get channelMessagesIds() {
			return channelMessagesIds;
		},
		get channelMessageId() {
			return channelMessageId;
		},
		get channelPinnedMessagesIds() {
			return channelPinnedMessagesIds;
		},
		get threadMessagesIds() {
			return threadMessagesIds;
		},
		get threadMessageId() {
			return threadMessageId;
		},
		get threadPinnedMessagesIds() {
			return threadPinnedMessagesIds;
		},
		changeGuildId,
		changeChannelId,
		changeThreadId,
		changeChannelMessageId,
		changeThreadMessageId,
		comboSetGuildChannel,
		comboSetGuildChannelMessage,
		getUrlState,
		pushState,
		replaceState,
	};
}


export function channelOrThreadIdToName(channelId: string) {
	if (!channelId) {
		return null
	}
	const channel = categories.flatMap(c => c.channels).find(c => c._id === channelId)
	if (channel) {
		return channel.name
	}
	const thread = categories.flatMap(c => c.channels).flatMap(c => c.threads).find(t => t._id === channelId)
	if (thread) {
		return thread.name
	}
	return null
}


async function restoreGuildState(state) {
	await guildState.changeGuildId(state.guild);
	await guildState.changeChannelId(state.channel);
	await guildState.changeThreadId(state.thread);
	await guildState.changeChannelMessageId(state.channelmessage);
	await guildState.changeThreadMessageId(state.threadmessage);

	await searchState.setSearchPrompt(state.search)
	await searchState.search(guildState.guildId)
	console.log("router - restored", state);
}

const guildState = getGuildState();
const layoutState = getLayoutState()
const searchState = getSearchState()

/**
 * Restore the state from the url on initial load
 */
let urlState = guildState.getUrlState();
await restoreGuildState(urlState);
await guildState.replaceState()  // set the initial state




/**
 * Listen for back/forward navigation events and restore the state
 */
window.addEventListener("popstate", async (e) => {
	if (e.state) {
		console.log("router - popped", e.state);
		await restoreGuildState(e.state);
	}
})


export function changeMessageId(channelOrThreadId: string, messageId: string) {
	if (isChannel(channelOrThreadId)) {
		guildState.changeChannelMessageId(messageId)
		guildState.pushState()
	}
	else if (isThread(channelOrThreadId)) {
		guildState.changeThreadMessageId(messageId)
		guildState.pushState()
	}
	else {
		console.warn('MessageTimestamp - unknown channel or thread id', channelOrThreadId)
	}
}