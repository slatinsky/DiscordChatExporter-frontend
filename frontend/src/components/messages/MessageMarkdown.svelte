<script lang="ts">
	import { checkUrl, darkenColor } from "src/js/helpers";
	import type { Emoji } from "src/js/interfaces";
    import { get } from "svelte/store";
    import { online } from "src/components/settings/settingsStore";
	import { searchPrompt } from "../search/searchStores";
	import { getChannelInfo, getRoleInfo } from "src/js/api";


    export let content: string
    // export let guild
    // export let message
    export let embed = false
    export let emotes: Emoji[] | null = null
    export let mentions: any[] | null = null
    export let guildId: string
    let processedContent: string

    const bubbleIcon = '<svg style="width:16px;height:16px;vertical-align: middle;margin-bottom: 0.2rem" class="icon-2Ph-Lv" aria-label="Message" aria-hidden="false" role="img" width="24" height="24" viewBox="0 0 24 24" fill="none"><path fill="currentColor" d="M4.79805 3C3.80445 3 2.99805 3.8055 2.99805 4.8V15.6C2.99805 16.5936 3.80445 17.4 4.79805 17.4H7.49805V21L11.098 17.4H19.198C20.1925 17.4 20.998 16.5936 20.998 15.6V4.8C20.998 3.8055 20.1925 3 19.198 3H4.79805Z"></path></svg>'
    const channelIcon = '<svg style="width:16px;height:16px;vertical-align: middle;margin-bottom: 0.2rem" width="24" height="24" viewBox="0 0 24 24" class="icon-2Ph-Lv" aria-label="Channel" aria-hidden="false" role="img"><path fill="currentColor" fill-rule="evenodd" clip-rule="evenodd" d="M5.88657 21C5.57547 21 5.3399 20.7189 5.39427 20.4126L6.00001 17H2.59511C2.28449 17 2.04905 16.7198 2.10259 16.4138L2.27759 15.4138C2.31946 15.1746 2.52722 15 2.77011 15H6.35001L7.41001 9H4.00511C3.69449 9 3.45905 8.71977 3.51259 8.41381L3.68759 7.41381C3.72946 7.17456 3.93722 7 4.18011 7H7.76001L8.39677 3.41262C8.43914 3.17391 8.64664 3 8.88907 3H9.87344C10.1845 3 10.4201 3.28107 10.3657 3.58738L9.76001 7H15.76L16.3968 3.41262C16.4391 3.17391 16.6466 3 16.8891 3H17.8734C18.1845 3 18.4201 3.28107 18.3657 3.58738L17.76 7H21.1649C21.4755 7 21.711 7.28023 21.6574 7.58619L21.4824 8.58619C21.4406 8.82544 21.2328 9 20.9899 9H17.41L16.35 15H19.7549C20.0655 15 20.301 15.2802 20.2474 15.5862L20.0724 16.5862C20.0306 16.8254 19.8228 17 19.5799 17H16L15.3632 20.5874C15.3209 20.8261 15.1134 21 14.8709 21H13.8866C13.5755 21 13.3399 20.7189 13.3943 20.4126L14 17H8.00001L7.36325 20.5874C7.32088 20.8261 7.11337 21 6.87094 21H5.88657ZM9.41045 9L8.35045 15H14.3504L15.4104 9H9.41045Z"></path></svg>'


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

        // remove empty strings
        terms = terms.filter(term => term.length > 0)

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
    async function process(content: string): void {
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

        // message links
        let regex = /target="_blank" href="https:\/\/discord(?:app)?\.com\/channels\/(\d+)\/(\d+)\/(\d+)">.*?</

        while (regex.test(processedContent)) {
            // get all message ids
            let matches = processedContent.match(regex)
            if (matches) {
                let messageId = matches[3]
                let channelId = matches[2]
                let guildId = matches[1]
                let fullMatch = matches[0]
                let channelInfo = await getChannelInfo(channelId)
                processedContent = processedContent.replace(fullMatch, `class="message-mention" href="/channels/${guildId.toString().padStart(24, '0')}/${channelId.toString().padStart(24, '0')}#${messageId.toString().padStart(24, '0')}">${channelIcon} ${channelInfo.name} › ${bubbleIcon}<`)
                console.log("processedContent", processedContent);
            }
        }

        // channel links
        regex = /target="_blank" href="https:\/\/discord(?:app)?\.com\/channels\/(\d+)\/(\d+)">.*?</
        while (regex.test(processedContent)) {
            // get all channel ids
            let matches = processedContent.match(regex)
            if (matches) {
                let channelId = matches[2]
                let guildId = matches[1]
                let fullMatch = matches[0]
                let channelInfo = await getChannelInfo(channelId)
                processedContent = processedContent.replace(fullMatch, `class="message-mention" href="/channels/${guildId.toString().padStart(24, '0')}/${channelId.toString().padStart(24, '0')}">${channelIcon} ${channelInfo.name}<`)
            }
        }

        if (mentions && mentions.length > 0) {
            mentions.forEach(mention => {
                processedContent = processedContent.replace(`@${mention.name}`, `<span class="message-mention">@${escapeHTML(mention.name)}#${escapeHTML(mention.discriminator)}</span>`)
                processedContent = processedContent.replace(`@${BigInt(mention._id)}`, `<span class="message-mention">@${escapeHTML(mention.name)}#${escapeHTML(mention.discriminator)}</span>`)
            })
        }

        if (guildId) {
            let channelRegex = /(?<!\d{17})#(\d{17,32})/   // negative lookahead checks if it is not channel link
            while (channelRegex.test(processedContent)) {
                let matches = processedContent.match(channelRegex)
                if (matches) {
                    let channelId = matches[1]
                    let fullMatch = matches[0]

                    let channelInfo = await getChannelInfo(channelId)
                    processedContent = processedContent.replace(fullMatch, `<a class="message-mention" href="/channels/${guildId}/${channelId.toString().padStart(24, '0')}">${channelIcon} ${channelInfo.name} </a>`)
                }
            }

            // roles
            let rolecRegex = /&(\d{17,32})/
            while (rolecRegex.test(processedContent)) {
                let matches = processedContent.match(rolecRegex)
                if (matches) {
                    let roleId = matches[1]
                    let fullMatch = matches[0]

                    let roleInfo = await getRoleInfo(roleId)
                    processedContent = processedContent.replace(fullMatch, `<span class="message-mention" style="color:${roleInfo.color};background-color:${darkenColor(roleInfo.color, .65)} !important">@${roleInfo.name}</span>`)
                }
            }
        }

        // highlight search terms
        // TEMPORARILY DISABLED - breaks links
        // if (highlight.length > 0) {
        //     highlight.forEach(term => {
        //         let regex = new RegExp(`(${term})`, 'gi')
        //         processedContent = processedContent.replace(regex, (match, p1) => {
        //             return `<span class="highlight">${p1}</span>`
        //         })
        //     })
        // }
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