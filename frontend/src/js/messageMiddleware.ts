

// collect message ids from multiple sources, aggregate them and fetch them in batches every 250ms

import { writable } from "svelte/store";
import type { Message } from "./interfaces"

const messages: Record<string, Message> = {}
const messageIdsToFetch: string[] = []
const MESSAGE_LIMIT_PER_FETCH = 250

// observer pattern using svelte store
export const justFetchedMessageIds: any = writable([])


async function fetchMessages(messageIds: string[]) {

	console.log("fetching " + messageIds.length + " messages");

	// fetch messages from server
	const response = await fetch("/api/messages", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(messageIds),
	})

	// parse response
	const messages_resp = await response.json()

	// add messages to cache
	for (const message of messages_resp) {
		messages[message._id] = message
	}

	justFetchedMessageIds.set(messageIds)
}

setInterval(() => {
	if (messageIdsToFetch.length === 0) {
		return
	}
	const messageIds = messageIdsToFetch.splice(0, MESSAGE_LIMIT_PER_FETCH)
	fetchMessages(messageIds)
}, 250)


// if we switch channel sooner than the messages are fetched, we no longer need it
// so we can remove it from the queue
export function cancelMessageContentRequest(messageId: string) {
	const index = messageIdsToFetch.indexOf(messageId)
	if (index > -1) {
		messageIdsToFetch.splice(index, 1)
	}
}


export async function getMessageContent(messageId: string): Promise<Message> {
	// if message is already loaded, return it
	if (messages[messageId]) {
		return new Promise((resolve) => {
			resolve(messages[messageId])
		})
	}

	// add message id to queue if it's not already there
	if (!messageIdsToFetch.includes(messageId)) {
		messageIdsToFetch.push(messageId)
	}

	// wait for message to be loaded asynchronously
	return new Promise((resolve, reject) => {
		// timeout after 10 seconds
		const timeout = setTimeout(() => {
			unsubscribe()
			reject("Error loading message_id " + messageId)
		}, 10000)
		const unsubscribe = justFetchedMessageIds.subscribe((messageIds: string[]) => {
			if (messageIds.includes(messageId)) {
				unsubscribe()
				clearTimeout(timeout)
				resolve(messages[messageId])
			}
		})
	})
}