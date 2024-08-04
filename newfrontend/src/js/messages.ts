import { dceToTwemoji } from "./emojis/dceToTwemoji";
import type { Message } from "./interfaces";
import { escapeRegExp } from "./markdownParser";

interface MessageCache {
    [messageId: string]: Message;
}


let messageCache: MessageCache = {};
let messageCacheWithoutReference: MessageCache = {};


async function _fetchMessagesFromApi(guildId: string | null, messageIds: string[]) {
    /**
     * Fetch messages from the API that are not already loaded in the cache
     */
    if (guildId === null) {
        guildId = "000000000000000000000000"
    }

    messageIds = messageIds.filter((messageId) => {
        return messageId !== "first" && messageId !== "last";
    })

    let notInCache = messageIds.filter((messageId) => {
        return !messageCacheWithoutReference[messageId];
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
    const containsFirst = messageIds.includes("first");
    const containsLast = messageIds.includes("last");
    console.log("api - fetching " + messageIds.length + " messages");
    if (messageIds.length === 0) {
        return [];
    }
    let nonReferenceMessages = await _fetchMessagesFromApi(guildId, messageIds);

    // replace unicode emojis with twemojis - TODO: move to preprocessor step
    for (const message of nonReferenceMessages) {
        for (const [key, value] of Object.entries(dceToTwemoji)) {
            const messageContent = message.content[0].content
            message.content[0].content = messageContent.replace(new RegExp(escapeRegExp(key), 'g'), value);
        }
    }
    // -

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

    if (containsFirst) {
        outMessages.unshift({_id: "first"});
    }
    if (containsLast) {
        outMessages.push({_id: "last"});
    }

    return outMessages;
}