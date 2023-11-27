<script lang="ts">
	import type { Channel, Emoji, Role } from "src/js/interfaces";
    import { online } from "src/components/settings/settingsStore";
	import { searchPrompt } from "../search/searchStores";
	import { parseMarkdown } from "src/js/markdownParser";


    export let content: string
    export let emotes: Emoji[] = []
    export let mentions: any[] = []
    export let roles: Role[] = []
    export let channels: Channel[] = []

    let hideMessageContent = false

    let processedHtml: string = ''
    let processedTree: any = {}


    // parse search terms from search prompt
    let terms: string[] = []
    function searchPromptChanged(newValue: string): void {
        // remove everything with `:` in it, we want to highlight only words
        // supports removal of values with quotes, like `from:"Deleted User#0000"`
        newValue = newValue.replaceAll(/\w+:".*?"|\w+:\w+|\w+:/gi, '')

        // remove all double spaces
        newValue = newValue.replaceAll(/\s{2,}/g, ' ')

        // remove all spaces at the beginning and end
        newValue = newValue.trim()

        // split by spaces to array
        let termsTemp = newValue.split(' ')

        // remove empty strings
        termsTemp = termsTemp.filter(term => term.length > 0)

        // apply highlight
        terms = termsTemp
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

    let bigEmojis = messageContainsOnlyEmojis(content)

    async function process(content: string, isOnline): void {
        // TEST STRING (uncomment to test formatter):
        // script is split up, because svelte tries to compile it
        // content = `# heading\n## subheading\n### subsubheading\n#### subsubsubheading\n##### subsubsubsubheading\n###### subsubsubsubsubheading\nhello @Adam old mention\nhello <@627848643557663699> new mention\n<t:1543392060>\n<t:1543392060:f>\n<b>UNSAFE HTML</><sc` + `ript>alert('this should never run')</scr` + `ipt>\nhttps://discord.com/channels/869237470565392384/869240824142102558\nhttps://discord.com/channels/869237470565392384/869240824142102558/869243917961408552\n**bold** *italic* ***bold italic*** __underline__ ~~strikethrough~~ __***underline bold italic***__ __**underline bold**__ __*underline italic*__ __***underline bold italic***__ __~~underline strikethrough~~__ __~~**underline strikethrough bold**~~__ __~~*underline strikethrough italic*~~__\n\n- list item1\n- list item2\n    - nested list item1\n- list item3\n\nhighlighted searchTerm1 searchTerm2 here\nnew <:kekw:782589696621805568> emoji\nnew <a:aPES_Blink:493677314735865856> animated emoji\nmentioned <@&878787663080666078> role`

        let parsed = parseMarkdown(content, {
            searchTerms: terms,
            mentions: mentions,
            emotes: emotes,
            roles: roles,
            channels: channels,
            onlyOffline: !isOnline,
        })
        processedTree = parsed.tree
        processedHtml = parsed.html

        // loop tree
        let bigEmojisTemp = true
        for (let node of processedTree) {
            for (const child of node?.content ?? []) {
                if (child?.type !== 'newEmoji') {
                    bigEmojisTemp = false
                }
            }
        }
        bigEmojis = bigEmojisTemp

        let hideMessageContentTemp = false
        for (let node of processedTree) {
            for (const child of node?.content ?? []) {
                if (child?.type === 'link') {
                    hideMessageContentTemp = true
                }
                else {
                    hideMessageContentTemp = false
                }
            }
        }
        hideMessageContent = hideMessageContentTemp
    }

    $: process(content, $online)
</script>


{#if !hideMessageContent}
    <span class:onlyemojis={bigEmojis} class="message-markdown">{@html processedHtml}</span>
    <!-- <button on:click={() => console.log(JSON.stringify(processedTree, null, 2))}>debug</button> -->
{/if}


<style>
    :global(.message-markdown) {
        line-height: 22px;
    }

    :global(.message-heading) {
        font-weight: 700;
        font-style: normal;
        margin: 0;
    }
    :global(.message-heading.h1) {
        margin-top: 8px;
        margin-bottom: 8px;
        line-height: 33px;
        font-size: 24px;
    }
    :global(.message-heading.h2) {
        margin-top: 16px;
        margin-bottom: 8px;
        font-size: 20px;
    }
    :global(.message-heading.h3) {
        margin-top: 16px;
        margin-bottom: 8px;
        font-size: 16px;
    }

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
    :global(.message-time) {
        color: #d1d4d6;
        background-color: #3A3C41;
        border-radius: 3px;
        padding: 0 2px;
    }
    :global(blockquote) {
        border-left: 5px solid #4F545C;
        margin: 1.5em 0px;
        padding: 0.5em 10px;
        width: 100%;
        border-radius: 4px;
    }

    :global(#search-results .message-highlight) {
        background-color: #6A5936;
        color: #fff;
        /* padding: 0px 2px; */
        /* border-radius: 4px; */
    }

    :global(.message-markdown ul) {
        margin: 4px 0 0 16px;
        padding: 0;
    }
    :global(.message-markdown li) {
        margin-bottom: 4px;
    }
    :global(.message-markdown .paragraph) {
    	white-space: pre-wrap
    }

</style>