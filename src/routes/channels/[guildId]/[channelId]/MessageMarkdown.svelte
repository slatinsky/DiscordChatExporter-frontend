<script>
    export let content
    export let guild
    let processedContent
    function process(content) {
        processedContent = window.discordMarkdown.toHTML(content);
        let regex = /:\w+:/g;
        // if regex matches, replace with emoji
        if (regex.test(processedContent)) {
            try {
                processedContent = processedContent.replace(regex, (match) => {
                    return `<img src="${Object.values(guild.emojis).find(emoji => emoji.name === match.slice(1, -1)).localFilePath}" alt="${match}" title="${match}" class="message-emoji">`
                })
            }
            catch (e) {
                console.log(e)
            }
        }

        // message links
        regex = /href="https:\/\/discord(?:app)?\.com\/channels\/(\d+)\/(\d+)\/(\d+)"/
        if (regex.test(processedContent)) {
            processedContent = processedContent.replace(regex, (match, guildId, channelId, messageId) => {
                return `href="/channels/${guildId.toString().padStart(24, '0')}/${channelId.toString().padStart(24, '0')}#${messageId.toString().padStart(24, '0')}"`
            })
            console.log(processedContent);
        }

        // channel links
        regex = /href="https:\/\/discord(?:app)?\.com\/channels\/(\d+)\/(\d+)"/
        if (regex.test(processedContent)) {
            processedContent = processedContent.replace(regex, (match, guildId, channelId) => {
                return `href="/channels/${guildId.toString().padStart(24, '0')}/${channelId.toString().padStart(24, '0')}"`
            })
            console.log(processedContent);
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
</style>