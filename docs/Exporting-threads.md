# Helper script to export forum posts in a channel

Viewing threads is supported by this viewer, but exporting them manually is time consuming. You can use this helper script to generate command to download all archived threads in a channel automatically:

### Steps
1. Open discord in browser (browser needs to be Chromium based - Chrome, Edge, Opera, Brave, Vivaldi, etc., not working in Firefox)
2. Navigate to channel with threads. Do not open thread list (if you opened it, refresh the page)
3. press F12 and paste this script to the console:

```js
len = 0
ids = []
previouseScrollTop = 0

// interceptor  https://stackoverflow.com/a/66564476
if (window.oldXHROpen === undefined) {
    window.oldXHROpen = window.XMLHttpRequest.prototype.open;
    window.XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
    this.addEventListener('load', function() {
        try {
            var json = JSON.parse(this.responseText);
            if (json.hasOwnProperty('threads')) {
                // get ids
                for (const thread of json.threads) {
                    ids.push(thread.id)
                }
            }
        }
        catch (e) {
            console.log(e)
        }
    });
    return window.oldXHROpen.apply(this, arguments);
    }
}
else {
    console.log('OK, interceptor already exists')
}


function getSelector(name) {
    if (name === 'thread-icon')
        return document.querySelectorAll('div[class*="toolbar-"] > div[aria-label="Threads"]')
    if (name === 'scroller-base')
        return document.querySelectorAll('div[id*="popout_"] > div > div > div[class*="scrollerBase-"]')
}

function clickThreadsIcon() {
    if (getSelector('scroller-base').length > 0) {
        console.log('OK, found scroller base (1)')
        mainFunc()
    }
    else if (getSelector('scroller-base').length == 0 && getSelector('thread-icon').length > 0) {
        getSelector('thread-icon')[0].click()
        console.log('OK, clicked Threads Icon')
        setTimeout(() => {
            if (getSelector('scroller-base').length == 0) {
                throw new Error('ERROR, could not find scroller-base')
            }
            else {
                console.log('OK, found scroller base (2)')
                mainFunc()
            }
        }, 1000)
    }
    else {
        throw new Error('ERROR, could not find threads icon')
    }
}
clickThreadsIcon()

function scrollToPosition(offset) {
    scrollDiv = getSelector('scroller-base')[0]
    scrollDiv.scroll(0, offset)
}

function captureIds() {
    ids = [...new Set(ids)]
    if (ids.length > len) {
        len = ids.length
        console.log('Found', len, 'IDs')
    }
}

function printIds() {
    console.log('DiscordChatExporter.Cli.exe export --token TOKEN --output "exports/threads" --format Json --media --reuse-media --markdown false --channel',ids.join(' '))
}

function mainFunc() {
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
        }, 500)
    }, 742)
}
```

4. script will scroll thread list. At the the end, it will print command to the console, which allows you to export all archived threads in the channel
5. edit command printed in the console (`--format`, `--output` and `--token`) and export with CLI version of DiscordChatExporter