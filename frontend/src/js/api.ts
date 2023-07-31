import type { Channel } from "./interfaces";

function createMockChannelInfo(channelId: string | undefined): Channel {
    return {
        "category":"Unknown category",
        "categoryId":"000000000000000000000000",
        "guildId":"000000000000000000000000",
        "msg_count":0,
        "name":"Unknown channel",
        "topic":null,
        "type":"GuildTextChat",
        "_id":channelId || "000000000000000000000000"
    };
}


export async function getChannelInfo(channelId: string): Promise<Channel> {
    if (!channelId) {
        return createMockChannelInfo(undefined);
    }
    const paddedChannelId = channelId.padStart(24, "0");
    const response = await fetch(`/api/channels?channel_id=${paddedChannelId}`);
    const json = await response.json();

    if (!json._id) {
        return createMockChannelInfo(channelId)
    }

    return json;
}
