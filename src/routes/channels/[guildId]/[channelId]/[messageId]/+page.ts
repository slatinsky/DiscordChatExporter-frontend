import { goto } from '$app/navigation';

export const prerender = false;
export const ssr = false;

export async function load({ params}) {
    goto(`/channels/${params.guildId}/${params.channelId}#${params.messageId}`);
}