<script lang="ts">
	import { checkUrl } from "src/js/helpers";
	import type { Emoji } from "src/js/interfaces";


    export let content: string
    // export let guild
    // export let message
    export let embed = false
    export let emotes: Emoji[] | null = null
    let processedContent: string

    function escapeHTML(unsafeText: string): string {  // source https://stackoverflow.com/a/48054293
        let div = document.createElement('div');
        div.innerText = unsafeText;
        return div.innerHTML;
    }
    function process(content: string): void {
        processedContent = window.discordMarkdown.toHTML(content, {embed});
        processedContent = processedContent.replaceAll('<a href=', '<a target="_blank" href=')  // open all links in new tab
        if (emotes) {
            for (let emote of emotes) {
                console.warn(emote.name, emote.image.path);
                console.log(processedContent);
                processedContent = processedContent.replaceAll(`:${emote.name}:`, `<img src="${checkUrl(emote.image)}" alt="${emote.name}" title="${emote.name}" class="message-emoji">`)
            }
        }

        // // message links
        let regex = /target="_blank" href="https:\/\/discord(?:app)?\.com\/channels\/(\d+)\/(\d+)\/(\d+)"/
        if (regex.test(processedContent)) {
            processedContent = processedContent.replace(regex, (match, guildId, channelId, messageId) => {
                return `href="/channels/${guildId.toString().padStart(24, '0')}/${channelId.toString().padStart(24, '0')}#${messageId.toString().padStart(24, '0')}"`
            })
        }

        // // channel links
        regex = /target="_blank" href="https:\/\/discord(?:app)?\.com\/channels\/(\d+)\/(\d+)"/
        if (regex.test(processedContent)) {
            processedContent = processedContent.replace(regex, (match, guildId, channelId) => {
                return `href="/channels/${guildId.toString().padStart(24, '0')}/${channelId.toString().padStart(24, '0')}"`
            })
        }

        // if (message.mentions && message.mentions.length > 0) {
        //     message.mentions.forEach(mention => {
        //         processedContent = processedContent.replace(`@${mention.name}`, `<span class="message-mention">@${escapeHTML(mention.name)}#${escapeHTML(mention.discriminator)}</span>`)
        //     })
        // }
    }

    $: process(content)
</script>

<span>{@html processedContent}</span>


<style>
    :global(.message-emoji) {
        width: 22px;
        height: 22px;
        transform: translate(0px, 2px);
    }
    :global(.message-mention) {
        color: #D4E0FC;
        background-color: #414675;
        font-weight: 500;
    }
    :global(blockquote) {
        border-left: 5px solid #4F545C;
        margin: 1.5em 0px;
        padding: 0.5em 10px;
        width: 100%;
        border-radius: 4px;
    }
</style>