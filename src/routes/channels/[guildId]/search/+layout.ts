export const prerender = false;
export const ssr = false;

export async function load({ params, parent }) {
    const { guild } = await parent();
    
    return {
        guildId: params.guildId,
        guild: guild
    };
}