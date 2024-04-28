let messageCache = {};

export async function messsageIdsToMessages(guild_id, messageIds) {
    console.log("api - fetching " + messageIds.length + " messages");
    if (messageIds.length === 0) {
        return [];
    }
    let messages = [];

    let notInCache = messageIds.filter((messageId) => {
        return !messageCache[messageId]
    })

    const response = await fetch(`/api/messages`, {
        method: "POST",
        headers: {
			"Content-Type": "application/json",
		},
        body: JSON.stringify({
			guild_id: guild_id,
			message_ids: messageIds
		})
    })

    const messages_resp = await response.json()

    for (const message of messages_resp) {
        messageCache[message._id] = message;
    }

    for (const messageId of messageIds) {
        messages.push(messageCache[messageId])
    }

    return messages;
}