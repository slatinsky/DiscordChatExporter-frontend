<script lang="ts">
	import { checkUrl } from "src/js/helpers";
	import type { Emoji } from "src/js/interfaces";
    import { get } from "svelte/store";
    import { online } from "src/routes/settingsStore";
	import { searchPrompt } from "../search/searchStores";



    export let content: string
    // export let guild
    // export let message
    export let embed = false
    export let emotes: Emoji[] | null = null
    export let mentions: any[] | null = null
    export let guildId: string
    let processedContent: string


    // highlight search terms
    let highlight: string[] = []
    function searchPromptChanged(newValue: string): void {
        // remove everything with `:` in it, we want to highlight only words
        // supports removal of values with quotes, like `from:"Deleted User#0000"`
        newValue = newValue.replaceAll(/\w+:".*?"|\w+:\w+|\w+:/gi, '')

        // remove all double spaces
        newValue = newValue.replaceAll(/\s{2,}/g, ' ')

        // remove all spaces at the beginning and end
        newValue = newValue.trim()

        // split by spaces to array
        let terms = newValue.split(' ')

        // apply highlight
        highlight = terms
    }
    $: $searchPrompt, searchPromptChanged($searchPrompt)

    function messageContainsOnlyEmojis(content: string): boolean {
        let regex = /<a?:\w+:\d{17,32}>/g
        let matches = content.match(regex)
        if (matches) {
            return matches.length === content.split(' ').length
        }
        return false
    }

    let onlyemojis = messageContainsOnlyEmojis(content)

    function escapeHTML(unsafeText: string): string {  // source https://stackoverflow.com/a/48054293
        let div = document.createElement('div');
        div.innerText = unsafeText;
        return div.innerHTML;
    }
    function process(content: string): void {
        if (emotes) {  // transform emotes to old format if exports were created using --markdown false
            for (let emote of emotes) {
                let regex = new RegExp(`<:${emote.name}:\\d{17,32}>`)
                if (regex.test(content)) {
                    content = content.replace(regex, `:${emote.name}:`)
                }
            }
        }

        processedContent = window.discordMarkdown.toHTML(content, {embed});
        processedContent = processedContent.replaceAll('<a href=', '<a target="_blank" href=')  // open all links in new tab
        if (emotes) {
            for (let emote of emotes) {
                processedContent = processedContent.replaceAll(`:${emote.name}:`, `<img src="${checkUrl(emote.image)}" alt="${emote.name}" title="${emote.name}" class="message-emoji">`)
            }
        }

        if (!get(online)){
            // If the emoji is not archived, discordMarkdown will transform it to a link - and that doesn't respect offline only setting in DCEF
            // to fix it, intentionally break the link if offline only mode set to true
            if (processedContent.includes('https://cdn.discordapp.com/emojis/')) {
                console.warn('intentionally breaking emoji link (https->hxxps), because you wish to view your exports offline only. If you want to view the emoji, please set the "offline only" setting to false.');
                processedContent = processedContent.replaceAll('https://cdn.discordapp.com/emojis/', 'hxxps://cdn.discordapp.com/emojis/')
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

        if (mentions && mentions.length > 0) {
            mentions.forEach(mention => {
                processedContent = processedContent.replace(`@${mention.name}`, `<span class="message-mention">@${escapeHTML(mention.name)}#${escapeHTML(mention.discriminator)}</span>`)
                processedContent = processedContent.replace(`@${BigInt(mention._id)}`, `<span class="message-mention">@${escapeHTML(mention.name)}#${escapeHTML(mention.discriminator)}</span>`)
            })
        }

        if (guildId) {
            let channelRegex = /#(\d{17,32})/g
            if (channelRegex.test(processedContent)) {
                processedContent = processedContent.replace(channelRegex, (match, channelId) => {
                    return `<a href="/channels/${guildId}/${channelId.toString().padStart(24, '0')}">#${channelId}</a>`
                })
            }
        }

        // highlight search terms
        if (highlight.length > 0) {
            highlight.forEach(term => {
                let regex = new RegExp(`(${term})`, 'gi')
                processedContent = processedContent.replace(regex, (match, p1) => {
                    return `<span class="highlight">${p1}</span>`
                })
            })
        }
    }

    $: process(content)
</script>

<span class:onlyemojis={onlyemojis}>{@html processedContent}</span>


<style>
    :global(.message-emoji),
    :global(.d-emoji) {
        width: 22px;
        height: 22px;
        transform: translate(0px, 2px);
    }

    :global(.onlyemojis .message-emoji),
    :global(.onlyemojis .d-emoji) {
        width: 50px;
        height: 50px;
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

    :global(#search-results .highlight) {
        background-color: #6A5936;
        color: #fff;
        /* padding: 0px 2px; */
        /* border-radius: 4px; */
    }
</style>