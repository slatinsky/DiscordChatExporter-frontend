import { get } from "svelte/store"
import { checkUrl, copyTextToClipboard } from "../../js/helpers"
import type { Author, Message } from "../../js/interfaces"
import { contextMenuItems } from "../../js/stores/menuStore"
import { linkHandler, setCurrentUser } from "../../js/stores/settingsStore"
import { selectedGuildId } from "../../js/stores/guildStore"


export function onUserRightClick(e, author: Author) {
    contextMenuItems.set([
        {
            "name": "View discord as this user",
            "action": () => {
                setCurrentUser(author._id, author.nickname, author.name, checkUrl(author.avatar))
            }
        },
        {
            "name": "Copy user ID",
            "action": () => {
                copyTextToClipboard(BigInt(author._id))
            }
        }
    ])
}


export function onMessageRightClick(e, message: Message) {
    contextMenuItems.set([
        {
            "name": `Open message in discord ${get(linkHandler) === 'app' ? "app" : "web"}`,
            "action": () => {
                window.open((get(linkHandler) === "app" ? "discord://" : "") + `https://discord.com/channels/${BigInt(get(selectedGuildId))}/${BigInt(message.channelId)}/${BigInt(message._id)}`,'_blank')
            }
        },
        {
            "name": "Copy message link",
            "action": () => {
                copyTextToClipboard(`https://discord.com/channels/${BigInt(get(selectedGuildId))}/${BigInt(message.channelId)}/${BigInt(message._id)}`);
            }
        },
        {
            "name": "Copy message ID",
            "action": () => {
                copyTextToClipboard(BigInt(message._id))
            }
        },
        {
            "name": "Print message object to devtools (F12)",
            "action": () => {
                console.log(JSON.stringify(message, null, 2))
            }
        }
    ])
}