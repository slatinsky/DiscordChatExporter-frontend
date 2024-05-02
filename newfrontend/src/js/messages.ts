import type { Message } from "./interfaces";

interface MessageCache {
    [messageId: string]: Message;
}


let messageCache: MessageCache = {};
let messageCacheWithoutReference: MessageCache = {};


async function _fetchMessagesFromApi(guildId: string, messageIds: string[]) {
    /**
     * Fetch messages from the API that are not already loaded in the cache
     */
    let notInCache = messageIds.filter((messageId) => {
        return !messageCacheWithoutReference[messageId]
    })

    if (notInCache.length > 0) {
        const response = await fetch(`/api/messages`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                guild_id: guildId,
                message_ids: notInCache
            })
        })
        const messages_resp = await response.json()
        for (const message of messages_resp) {
            messageCacheWithoutReference[message._id] = message;
        }
    }

    return messageIds.map((messageId) => messageCacheWithoutReference[messageId]);
}


export async function messsageIdsToMessages(guildId: string, messageIds: string[]) {
    console.log("api - fetching " + messageIds.length + " messages");
    if (messageIds.length === 0) {
        return [];
    }
    let nonReferenceMessages = await _fetchMessagesFromApi(guildId, messageIds);

    let referenceIdsToFetch = [];
    for (const message of nonReferenceMessages) {
        if (message.reference && message.reference.messageId) {
            if ( !messageCache[message.reference.messageId] ) {
                referenceIdsToFetch.push(message.reference.messageId);
            }
        }
    }

    console.log("api - fetching " + referenceIdsToFetch.length + " referenced messages");
    let referencedMessages = await _fetchMessagesFromApi(guildId, referenceIdsToFetch); // as a side effect, this will populate messageCache with the referenced messages

    let outMessages = []
    for (const message of nonReferenceMessages) {
        let messageCopy = JSON.parse(JSON.stringify(message));
        if (messageCopy.reference && messageCopy.reference.messageId) {
            messageCopy.referencedMessage = messageCacheWithoutReference[message.reference.messageId];
        }
        outMessages.push(messageCopy);
    }

    return outMessages;
}