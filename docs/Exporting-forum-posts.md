# Helper script to export forum posts in a channel

Viewing forums is supported by this viewer, but exporting them manually is time consuming. You can use this helper script to generate command to download all forum posts in a forum channel automatically:

### Steps
1. Open discord in browser (browser needs to be Chromium based - Chrome, Edge, Opera, Brave, Vivaldi, etc., not working in Firefox)
2. Navigate to channel with forum post list
3. press F12 and paste this script to the console:

```js
len = 0
ids = []
previouseScrollTop = 0

function scrollToPosition(offset) {
    scrollDiv = document.querySelector('div[class*="chat-"] > div > div > div[class*="scrollerBase-"]')
    scrollDiv.scroll(0, offset)
}

function captureIds() {
    document.querySelectorAll('div[data-item-id]').forEach((e) => ids.push(e.dataset.itemId))
    ids = [...new Set(ids)]
    if (ids.length > len) {
        len = ids.length
        console.log('Found', len, 'IDs')
    }
}

function printIds() {
    console.log('DiscordChatExporter.Cli.exe export --token TOKEN --output "exports/forums" --format Json --media --reuse-media --markdown false --channel',ids.join(' '))
}

scrollToPosition(0)
interval = setInterval(() => {
    scrollToPosition(scrollDiv.scrollTop + window.innerHeight / 3)
    setTimeout(() => {
        captureIds()
        if (previouseScrollTop === scrollDiv.scrollTop) {
            clearInterval(interval)
            printIds()
        }
        previouseScrollTop = scrollDiv.scrollTop
    }, 1000)
}, 1542)
```

4. script will scroll the page. At the the end, it will print command to the console, which allows you to export all forum posts in the forum channel
5. edit command printed in the console (`--format`, `--output` and `--token`) and export with CLI version of DiscordChatExporter