<script>
    import {checkUrl } from '../../../../helpers';

    export let content
    export let guild
    export let message
    let processedContent

    function escapeHTML(unsafeText) {  // source https://stackoverflow.com/a/48054293
        let div = document.createElement('div');
        div.innerText = unsafeText;
        return div.innerHTML;
    }
    function process(content) {
        processedContent = window.discordMarkdown.toHTML(content);
        let regex = /:\w+:/g;
        // if regex matches, replace with emoji
        if (regex.test(processedContent)) {
            try {
                processedContent = processedContent.replace(regex, (match) => {
                    return `<img src="${checkUrl(Object.values(guild.emojis).find(emoji => emoji.name === match.slice(1, -1)).imageUrl?.url)}" alt="${match}" title="${match}" class="message-emoji">`
                })
            }
            catch (e) {
                console.warn("emojis not found", processedContent.match(regex));
            }
        }

        // message links
        regex = /href="https:\/\/discord(?:app)?\.com\/channels\/(\d+)\/(\d+)\/(\d+)"/
        if (regex.test(processedContent)) {
            processedContent = processedContent.replace(regex, (match, guildId, channelId, messageId) => {
                return `href="/channels/${guildId.toString().padStart(24, '0')}/${channelId.toString().padStart(24, '0')}#${messageId.toString().padStart(24, '0')}"`
            })
        }

        // channel links
        regex = /href="https:\/\/discord(?:app)?\.com\/channels\/(\d+)\/(\d+)"/
        if (regex.test(processedContent)) {
            processedContent = processedContent.replace(regex, (match, guildId, channelId) => {
                return `href="/channels/${guildId.toString().padStart(24, '0')}/${channelId.toString().padStart(24, '0')}"`
            })
        }

        if (message.mentions && message.mentions.length > 0) {
            message.mentions.forEach(mention => {
                processedContent = processedContent.replace(`@${mention.name}`, `<span class="message-mention">@${escapeHTML(mention.name)}#${escapeHTML(mention.discriminator)}</span>`)
            })
        }
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