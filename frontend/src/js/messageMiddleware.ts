

// collect message ids from multiple sources, aggregate them and fetch them in batches every 250ms

import type { Message } from "./interfaces"

const messages: Record<string, Message> = {}
const messageIdsToFetch: string[] = []


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
}

setInterval(() => {
	if (messageIdsToFetch.length === 0) {
		return
	}
	const messageIds = messageIdsToFetch.splice(0, 50)
	fetchMessages(messageIds)
}, 250)


// fetch messages in the background every 250ms
// wait for fetch to finish before continuing
// #### this approach may be faster, but BROWSER CAN'T KEEP UP RENDERING THEM AT THIS SPEED ####
// async function fetchLoop() {
// 	console.log("fetch loop started");
// 	while (true) {
// 		if (messageIdsToFetch.length === 0) {
// 			await new Promise((resolve) => setTimeout(resolve, 250))
// 			continue
// 		}
// 		const messageIds = messageIdsToFetch.splice(0, 50)
// 		await fetchMessages(messageIds)
// 		await new Promise((resolve) => setTimeout(resolve, 25))
// 	}
// }

// fetchLoop()



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
		let counter = 0
		const interval = setInterval(() => {
			if (messages[messageId]) {
				clearInterval(interval)
				resolve(messages[messageId])
			}
			counter++
			if (counter > 100) {
				clearInterval(interval)
				reject("Error loading message_id " + messageId)
			}
		}, 100)
	})
}