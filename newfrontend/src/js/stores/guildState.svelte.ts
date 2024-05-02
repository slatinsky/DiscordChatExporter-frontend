import { fetchCategoriesChannelsThreads, fetchGuilds, fetchMessageIds } from "./api";
import { threadshown } from "./layoutStore";

let guilds = $state(await fetchGuilds());
let guildId = $state(null);
let guild = $derived(guilds.find(g => g._id === guildId) || null);

let channelId = $state(null);
let categories = $state([]);
let channel = $derived(categories.flatMap(c => c.channels).find(c => c._id === channelId) || null);
let channelMessageId = $state(null);
let channelMessagesIds = $state([]);

let threadId = $state(null);
let thread = $derived(categories.flatMap(c => c.channels).flatMap(c => c.threads).find(t => t._id === threadId) || null);
let threadMessageId = $state(null);
let threadMessagesIds = $state([]);


export function isChannel(channelId: string) {
	return categories.flatMap(c => c.channels).find(c => c._id === channelId) !== undefined
}


export function getGuildState() {
	async function changeGuildId(newGuildId: string | null) {
		console.log("newGuildState -", guilds);
		if (guildId === newGuildId) {
			return;
		}
		guildId = newGuildId;
		await changeChannelId(null)
		categories = await fetchCategoriesChannelsThreads(guildId)
	}

	async function changeChannelId(newChannelId: string | null) {
		if (channelId === newChannelId) {
			return;
		}
		channelId = newChannelId;
		await changeThreadId(null)

		if (newChannelId && guildId) {
			channelMessagesIds = await fetchMessageIds(guildId, newChannelId)
			channelMessageId = channelMessagesIds.length > 0 ? channelMessagesIds[-1] : null  // last message
		}
		else {
			channelMessagesIds = []
			channelMessageId = null
		}
		console.log("newGuildState -", guilds);
	}

	async function changeThreadId(newThreadId: string | null) {
		if (threadId === newThreadId) {
			return;
		}
		threadId = newThreadId;
		if (newThreadId && guildId) {
			threadMessagesIds = await fetchMessageIds(guildId, newThreadId)
			threadMessageId = threadMessagesIds.length > 0 ? threadMessagesIds[-1] : null  // last message

			threadshown.set(true)  // TODO: migrate to runes
		}
		else {
			threadMessagesIds = []
			threadMessageId = null

			threadshown.set(false)  // TODO: migrate to runes
		}
	}

	async function changeChannelMessageId(newMessageId: string | null) {
		channelMessageId = newMessageId
	}

	async function changeThreadMessageId(newMessageId: string | null) {
		threadMessageId = newMessageId
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
		get threadMessagesIds() {
			return threadMessagesIds;
		},
		get threadMessageId() {
			return threadMessageId;
		},
		changeGuildId,
		changeChannelId,
		changeThreadId,
		changeChannelMessageId,
		changeThreadMessageId
	};
}


let restoringState = true;
async function restoreGuildState(state) {
	restoringState = true;
	await guildState.changeGuildId(urlState.guild);
	await guildState.changeChannelId(urlState.channel);
	await guildState.changeThreadId(urlState.thread);
	await guildState.changeChannelMessageId(urlState.channelmessage);
	await guildState.changeThreadMessageId(urlState.threadmessage);
	restoringState = false;
	console.log("router - restored state", state);
}

// todo: restore from url
const guildState = getGuildState();
let urlState = getUrlState();
await restoreGuildState(urlState);



function getUrlState() {
	const urlParams = new URLSearchParams(window.location.search)
	let state = {
		guild: urlParams.get("guild") || null,
		channel: urlParams.get("channel") || null,
		thread: urlParams.get("thread") || null,
		channelmessage: urlParams.get("channelmessage") || null,
		threadmessage: urlParams.get("threadmessage") || null
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


function getRuneState() {
	return {
		guild: guildId || null,
		channel: channelId || null,
		thread: threadId || null,
		channelmessage: channelMessageId || null,
		threadmessage: threadMessageId || null
	}
}

function saveStateToUrl() {
	let state: any = getRuneState()
	let nonNullState: any = {}  // pretty url without null values
	for (const key in state) {
		if (state[key] !== null && state[key] !== undefined) {
			nonNullState[key] = state[key]
		}
	}
	const searchParams = new URLSearchParams(nonNullState);
	const getParams = searchParams.toString()
	window.history.pushState(state, "", `/?${getParams}`)
}


function isObjectEqual(a: any, b: any) {
	return JSON.stringify(a) === JSON.stringify(b)
}


window.addEventListener("popstate", async (e) => {
	if (restoringState) {
		return
	}
	await restoreGuildState(e.state);
})

// TODO: there has to be a better way to check for changes
setInterval(() => {
	let newUrlState = getUrlState()
	let newRuneState = getRuneState()
	if (!isObjectEqual(newUrlState, newRuneState)) {
		console.log("router - changes detected", newRuneState, newUrlState)
		saveStateToUrl()
	}
}, 1000);
