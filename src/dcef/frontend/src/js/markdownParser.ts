// TODO: external links should be opened in a new tab

import SimpleMarkdown from 'simple-markdown';
import { renderTimestamp } from './time';
import { checkUrl } from './helpers';
import hljs from 'highlight.js';
import { twemojiToFilename } from './emojis/twemojiToFilename';
import type { Asset } from './interfaces';

export function escapeRegExp(string: string) {
    // https://stackoverflow.com/a/6969486
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}
function escapeRegExpForOrSearch(string: string) {
    // escape only | and ^
    // if the regex is still valid, use it, otherwise escape everything
    let lessStrict = string.replace(/[\^\|]/g, '\\$&')
    let moreStrict = escapeRegExp(string)
    if (isRegexValid(lessStrict)) {
        return lessStrict
    }
    else {
        return moreStrict
    }
}
function isRegexValid(regex: string) {
    try {
        new RegExp(regex);
        return true;
    } catch (e) {
        return false;
    }
}


const CHANNEL_ICON = `<svg style="width: 1rem;height: 1rem;vertical-align: middle;margin-bottom: .2rem;margin-right:4px" width="24" height="24" viewBox="0 0 24 24" role="img"><path fill="currentColor" fill-rule="evenodd" clip-rule="evenodd" d="M5.88657 21C5.57547 21 5.3399 20.7189 5.39427 20.4126L6.00001 17H2.59511C2.28449 17 2.04905 16.7198 2.10259 16.4138L2.27759 15.4138C2.31946 15.1746 2.52722 15 2.77011 15H6.35001L7.41001 9H4.00511C3.69449 9 3.45905 8.71977 3.51259 8.41381L3.68759 7.41381C3.72946 7.17456 3.93722 7 4.18011 7H7.76001L8.39677 3.41262C8.43914 3.17391 8.64664 3 8.88907 3H9.87344C10.1845 3 10.4201 3.28107 10.3657 3.58738L9.76001 7H15.76L16.3968 3.41262C16.4391 3.17391 16.6466 3 16.8891 3H17.8734C18.1845 3 18.4201 3.28107 18.3657 3.58738L17.76 7H21.1649C21.4755 7 21.711 7.28023 21.6574 7.58619L21.4824 8.58619C21.4406 8.82544 21.2328 9 20.9899 9H17.41L16.35 15H19.7549C20.0655 15 20.301 15.2802 20.2474 15.5862L20.0724 16.5862C20.0306 16.8254 19.8228 17 19.5799 17H16L15.3632 20.5874C15.3209 20.8261 15.1134 21 14.8709 21H13.8866C13.5755 21 13.3399 20.7189 13.3943 20.4126L14 17H8.00001L7.36325 20.5874C7.32088 20.8261 7.11337 21 6.87094 21H5.88657ZM9.41045 9L8.35045 15H14.3504L15.4104 9H9.41045Z"></path></svg>`;

const NO_ACCESS_ICON = `<svg style="width: 1rem;height: 1rem;vertical-align: middle;margin-bottom: .2rem;margin-right:4px" width="24" height="24" viewBox="0 0 24 24" aria-label="No Access" aria-hidden="false" role="img"><path fill="currentColor" d="M17 11V7C17 4.243 14.756 2 12 2C9.242 2 7 4.243 7 7V11C5.897 11 5 11.896 5 13V20C5 21.103 5.897 22 7 22H17C18.103 22 19 21.103 19 20V13C19 11.896 18.103 11 17 11ZM12 18C11.172 18 10.5 17.328 10.5 16.5C10.5 15.672 11.172 15 12 15C12.828 15 13.5 15.672 13.5 16.5C13.5 17.328 12.828 18 12 18ZM15 11H9V7C9 5.346 10.346 4 12 4C13.654 4 15 5.346 15 7V11Z" aria-hidden="true"></path></svg>`

const CHEVRON_ICON = `<svg style="width: 0.5rem;height: 0.5rem;margin-left: 4px;margin-right: 6px;margin-bottom: 1px" role="img" width="24" height="24" viewBox="0 0 24 24"><g fill="none" fill-rule="evenodd"><polygon fill="currentColor" fill-rule="nonzero" points="8.47 2 6.12 4.35 13.753 12 6.12 19.65 8.47 22 18.47 12"></polygon><polygon points="0 0 24 0 24 24 0 24"></polygon></g></svg>`;

const MESSAGEBUBBLE_ICON = `<svg style="width:1rem;height:1rem;vertical-align: middle;margin-bottom: 0.2rem;" role="img" width="24" height="24" viewBox="0 0 24 24" fill="none"><path fill="currentColor" d="M4.79805 3C3.80445 3 2.99805 3.8055 2.99805 4.8V15.6C2.99805 16.5936 3.80445 17.4 4.79805 17.4H7.49805V21L11.098 17.4H19.198C20.1925 17.4 20.998 16.5936 20.998 15.6V4.8C20.998 3.8055 20.1925 3 19.198 3H4.79805Z"></path></svg>`;

const ASSET_ICON = `<svg style="width:1rem;height:1rem;vertical-align: middle;margin-bottom: 0.2rem;" role="img" width="16" height="16" fill="none" viewBox="0 0 24 24"><path fill="currentColor" d="M10.57 4.01a6.97 6.97 0 0 1 9.86 0l.54.55a6.99 6.99 0 0 1 0 9.88l-7.26 7.27a1 1 0 0 1-1.42-1.42l7.27-7.26a4.99 4.99 0 0 0 0-7.06L19 5.43a4.97 4.97 0 0 0-7.02 0l-8.02 8.02a3.24 3.24 0 1 0 4.58 4.58l6.24-6.24a1.12 1.12 0 0 0-1.58-1.58l-3.5 3.5a1 1 0 0 1-1.42-1.42l3.5-3.5a3.12 3.12 0 1 1 4.42 4.42l-6.24 6.24a5.24 5.24 0 0 1-7.42-7.42l8.02-8.02Z" class=""></path></svg>`





// new roles
// <@&878787663080666078>

const newRole = {
    order: SimpleMarkdown.defaultRules.text.order - 0.5,
    match: function(source, state, lookbehind) {
        return /^<@&(\d{17,24})>/.exec(source);
    },
    parse: function(capture, recurseParse, state) {
        let roleId = capture[1].toString().padStart(24, '0')
        let roleName = "role"
        let roleColor = "#D4E0FC"
        let backgroundColor = "#414675"
        for (const role of state.roles) {
            if (role._id == roleId) {
                roleName = role.name
                if (role.color !== null) {
                    roleColor = role.color
                    backgroundColor = role.color + "15"
                }
            }
        }
        return {
            type: 'newRole',
            roleId: roleId,
            roleName: roleName,
            roleColor: roleColor,
            backgroundColor: backgroundColor,
        };
    },
    html: function(node, recurseOutput, state) {
        return `<span class="message-mention" style="color: ${node.roleColor};background-color: ${node.backgroundColor}">@${node.roleName}</span>`;
    }
}


// old mentions

const oldMention = {
    order: SimpleMarkdown.defaultRules.text.order - 0.49,
    match: function(source, state, lookbehind) {
        if (state.mentions.length === 0) {
            return null;
        }
        let searchTerms = state.mentions.map((term: string) => escapeRegExpForOrSearch(term.nickname));
        return new RegExp(`^@(${searchTerms.join("|")})`, 'i').exec(source);
    },
    parse: function(capture, recurseParse, state) {
        return {
            type: 'mention',
            username: capture[1]
        };
    },
    html: function(node, recurseOutput, state) {
        return `<span class="message-mention" href="${node.username}">@${node.username}</span>`;
    },
}


// new mentions
// <@123>

const newMention = {
    order: SimpleMarkdown.defaultRules.text.order - 0.48,
    match: function(source, state, lookbehind) {
        return /^<@!?(\d{17,24})>/.exec(source);
    },
    parse: function(capture, recurseParse, state) {
        let mentionId = capture[1].toString().padStart(24, '0')
        let mentionNickName = null
        for (const mention of state.mentions) {
            if (mention._id == mentionId) {
                mentionNickName = mention.nickname
            }
        }
        return {
            type: 'newMention',
            userId: capture[1],
            nickName: mentionNickName
        };
    },
    html: function(node, recurseOutput, state) {
        if (node.nickName == null) {
            return `<span class="message-mention" data-userid="${node.userId}">&lt;@${node.userId}&gt;</span>`;
        }
        return `<span class="message-mention" data-userid="${node.userId}">@${node.nickName}</span>`;
    }
}


// new channels
// <#123>

const newChannel = {
    order: SimpleMarkdown.defaultRules.text.order - 0.48,
    match: function(source, state, lookbehind) {
        return /^<#(\d{17,24})>/.exec(source);
    },
    parse: function(capture, recurseParse, state) {
        let channelName = "channel"
        let channelId = capture[1]
        let paddedChannelId = channelId.toString().padStart(24, '0')
        let guildId = null
        for (const channel of state.channels) {
            if (channel._id == paddedChannelId) {
                channelName = channel.name
                guildId = channel.guildId
            }
        }
        return {
            type: 'newChannel',
            channelId: channelId,
            paddedChannelId: paddedChannelId,
            channelName: channelName,
            guildId: guildId,
        };
    },
    html: function(node, recurseOutput, state) {
        if (node.guildId == null) {
            return `<span class="message-mention" data-channelid="${node.channelId}">${NO_ACCESS_ICON} No Access</span>`;
        }
        else {
            return `<a class="message-mention" onclick="window.globalSetChannel('${node.guildId}', '${node.paddedChannelId}')"  href="javascript:void(0)">${CHANNEL_ICON} ${node.channelName}</a>`;
        }
    }
}


// timestamps
// possible timestamp types (https://gist.github.com/LeviSnoot/d9147767abeef2f770e9ddcd91eb85aa):
// Default	        <t:1543392060>    November 28, 2018 9:01 AM             28 November 2018 09:01
// Short Time       <t:1543392060:t>  9:01 AM                               09:01
// Long Time        <t:1543392060:T>  9:01:00 AM                            09:01:00
// Short Date       <t:1543392060:d>  11/28/2018                            28/11/2018
// Long Date        <t:1543392060:D>  November 28, 2018                     28 November 2018
// Short Date/Time  <t:1543392060:f>  November 28, 2018 9:01 AM             28 November 2018 09:01
// Long Date/Time   <t:1543392060:F>  Wednesday, November 28, 2018 9:01 AM  Wednesday, 28 November 2018 09:01
// Relative Time    <t:1543392060:R>  3 years ago                           3 years ago

const timestamp = {
  order: SimpleMarkdown.defaultRules.text.order - 0.6,
  match: function(source, state, lookbehind) {
      return /^<t:(\d{1,10})(?::([tTdfFR]))?>/.exec(source);
  },
  parse: function(capture, recurseParse, state) {
      return {
          type: 'timestamp',
          timestamp: capture[1]
      };
  },
  html: function(node, recurseOutput, state) {
      let timeString = renderTimestamp(node.timestamp * (1000))
      return `<span class="message-time" href="${node.timestamp}">${timeString}</span>`;
  },
}


// message links
// https://discord.com/channels/123/456/789

const messageLink = {
  order: SimpleMarkdown.defaultRules.autolink.order - 0.5,
  match: function(source, state, lookbehind) {
      return /^https:\/\/discord(?:app)?\.com\/channels\/(\d{17,24})\/(\d{17,24})\/(\d{17,24})/.exec(source);
  },
  parse: function(capture, recurseParse, state) {
      return {
          type: 'messageLink',
          guildId: capture[1].toString().padStart(24, '0'),
          channelId: capture[2].toString().padStart(24, '0'),
          messageId: capture[3].toString().padStart(24, '0'),
          url: capture[0]
      };
  },
  html: function(node, recurseOutput, state) {
      return `<a class="message-mention" onclick="window.globalSetMessage('${node.guildId}', '${node.channelId}', '${node.messageId}')"  href="javascript:void(0)">${CHANNEL_ICON} message link ${CHEVRON_ICON}${MESSAGEBUBBLE_ICON}</a>`;
  },
}


// channel links
// https://discord.com/channels/123/456

const channelLink = {
  order: SimpleMarkdown.defaultRules.autolink.order - 0.4,
  match: function(source, state, lookbehind) {
      return /^https:\/\/discord(?:app)?\.com\/channels\/(\d{17,24})\/(\d{17,24})/.exec(source);
  },
  parse: function(capture, recurseParse, state) {
      return {
          type: 'channelLink',
          guildId: capture[1].toString().padStart(24, '0'),
          channelId: capture[2].toString().padStart(24, '0'),
          url: capture[0]
      };
  },
  html: function(node, recurseOutput, state) {
      return `<a class="message-mention" onclick="window.globalSetChannel('${node.guildId}', '${node.channelId}')" href="javascript:void(0)">${CHANNEL_ICON} channel link</a>`;
  },
}

// pretty asset links
// https://cdn.discordapp.com/attachments/12345678900000000/12345678900000000/image.png
// https://cdn.discordapp.com/attachments/12345678900000000/12345678900000000/image.png?ex=658f3e1d&is=657cc91d&hm=b32dbaf1dc2a47ccc2d547e1ec0aedc1ba51e9a8ce4137acf4fb98c84ede4cb8&
// https://media.discordapp.net/attachments/12345678900000000/12345678900000000/image.png?ex=658f3e1d&is=657cc91d&hm=b32dbaf1dc2a47ccc2d547e1ec0aedc1ba51e9a8ce4137acf4fb98c84ede4cb8&

const assetLink = {
  order: SimpleMarkdown.defaultRules.autolink.order - 0.39,
  match: function(source, state, lookbehind) {
      return /^https:\/\/(?:media\.discordapp\.net|cdn\.discordapp\.com)\/attachments\/\d{17,24}\/\d{17,24}\/([^ \n\?]+)(?:\?[^ \n]+)?/.exec(source);
    },
    parse: function(capture, recurseParse, state) {
        return {
            type: 'assetLink',
            url: capture[0],
            filename: capture[1]
        };
    },
    html: function(node, recurseOutput, state) {
        return `<a class="message-mention" href="${node.url}" target="_blank">${ASSET_ICON} ${node.filename}</a>`;
    }
}

// headings
// # Heading
// ## Heading
// ### Heading
// more than 3 # are not supported by discord

const customHeading = {
  order: SimpleMarkdown.defaultRules.heading.order - 0.1,
  match: function(source, state, lookbehind) {
    // previous match must not end with #
    if (lookbehind !== null && lookbehind[lookbehind.length - 1] == "#") {
        return null;
    }
    return /^ *(?<!\#)(#{1,3}) ([^\n]+?)#* *(?![^\n])/.exec(source);
  },
  parse: function(capture, recurseParse, state) {
      return {
          type: 'customHeading',
          level: capture[1].length,
          content: capture[2]
      };
  },
  html: function(node, recurseOutput, state) {
      return `<div class="message-heading h${node.level}">${node.content}</div>`;
  },
}


// old emojis
// :kekw:

const oldEmoji = {
  order: SimpleMarkdown.defaultRules.autolink.order - 0.31,
  match: function(source, state, lookbehind) {
      if (state.emotes.length === 0) {
          return null;
      }
      let searchTerms = state.emotes.map((term: string) => escapeRegExpForOrSearch(term.name));
      return new RegExp(`^:(${searchTerms.join("|")}):`, 'i').exec(source);
  },
  parse: function(capture, recurseParse, state) {
    let url = null
    if (!state.onlyOffline) {
        // fallback online url if offline mode is not enforced
        url = `https://cdn.discordapp.com/emojis/${capture[3]}`
    }
    let emojiName = capture[1]
    for (const emote of state.emotes) {
        console.log("emote", emote)
        if (emote.name == emojiName) {
            const newUrl = checkUrl(emote.image)
            if (newUrl !== "") {
                url = newUrl
            }
        }
    }
    return {
        type: 'oldEmoji',
        name: emojiName,
        url: url,
    };
  },
  html: function(node, recurseOutput, state) {
    if (node.url == null) {
        return `<span class="message-emoji">:${node.name}:</span>`;
    }
    else {
        return `<img class="message-emoji" src="${node.url}" alt="${node.name}">`;
    }
  },
}


// TODO: there HAS to be a better way to do this
function openInGalleryTemplate(asset: Asset) {
    if (asset == null) {
        return "javascript:void(0)";
    }
    return `globalShowSingleAsset(JSON.parse(decodeURIComponent(escape(atob('${btoa(unescape(encodeURIComponent(JSON.stringify(asset))))}')))))`;
}

// new emojis
// <:kekw:782589696621805568>
// <a:kekw:782589696621805568>

const newEmoji = {
  order: SimpleMarkdown.defaultRules.autolink.order - 0.3,
  match: function(source, state, lookbehind) {
      return /^<(a)?:(\w{2,32}):(\d{17,24})>/.exec(source);
  },
  parse: function(capture, recurseParse, state) {
    const isAnimated = capture[1] === 'a'
    const emojiName = capture[2]
    const emojiId = capture[3]
    let imageObj = null
    const paddedEmojiId = emojiId.toString().padStart(24, '0')
    let url = null
    if (!state.onlyOffline) {
        // fallback online url if offline mode is not enforced
        url = `https://cdn.discordapp.com/emojis/${capture[3]}`
    }
    for (const emote of state.emotes) {
        if (emote._id == paddedEmojiId) {
            const newUrl = checkUrl(emote.image)
            if (newUrl !== "") {
                url = newUrl
            }
            imageObj = emote.image
        }
    }
    return {
        type: 'newEmoji',
        animated: isAnimated,
        name: emojiName,
        url: url,
        imageObj: imageObj
    };
  },
  html: function(node, recurseOutput, state) {
    if (node.url == null) {
        return `<span class="message-emoji">:${node.name}:</span>`;
    }
    else {
        return `<img class="message-emoji" src="${node.url}" title=":${node.name}:" alt="${node.name}" onclick="${openInGalleryTemplate(node.imageObj)}" style="cursor:pointer" >`;
    }
  },
}


// text spoiler
// ||spoiler||

const textSpoiler = {
  order: SimpleMarkdown.defaultRules.text.order - 0.2,
  match: function(source, state, lookbehind) {
      return /^\|\|(.+?)\|\|/.exec(source);
  },
  parse: function(capture, recurseParse, state) {
      return {
          type: 'twemoji',
          content: capture[1],
      };
  },
  html: function(node, recurseOutput, state) {
      return `<span class="twemoji">${node.content}</span>`;
  },
}



const twemoji = {
    order: SimpleMarkdown.defaultRules.text.order - 0.15,
    match: function(source, state, lookbehind) {
        return /^(:[a-zA-Z0-9_]+:)/.exec(source);
    },
    parse: function(capture, recurseParse, state) {
        return {
            type: 'twemoji',
            content: capture[1],
            twemojiFilename: twemojiToFilename[capture[1]],  // twemojiToFilename - key is :emojiname:, value is filename without `.svg`
        };
    },
    html: function(node, recurseOutput, state) {
        if (node.twemojiFilename == null) {  // emoji file not found
            return `<span class="twemoji">${node.content}</span>`;
        }
        return `<img src="/twemoji-svg/${node.twemojiFilename}.svg" alt="${node.content}" class="twemoji" width="22" height="22" title="${node.content}">`;
    },
}


// highlight search terms from search results (state.searchTerms)

const highlightSearchTerms = {
  order: SimpleMarkdown.defaultRules.text.order - 0.1,
  match: function(source, state, lookbehind) {
    // escaping regex is needed to prevent infinite loops
    let searchTerms = state.searchTerms.map((term: string) => escapeRegExpForOrSearch(term));
    if (searchTerms.length === 0) {
        return null;
    }

    return new RegExp(`^(.*?)(?<!\>)(${searchTerms.join("|")})`, 'i').exec(source);
},
parse: function(capture, recurseParse, state) {
      return {
          type: 'highlightSearchTerms',
          textBefore: capture[1],
          searchTerm: capture[2],
      };
  },
  html: function(node, recurseOutput, state) {
      return `${node.textBefore}<span class="message-highlight">${node.searchTerm}</span>`;
  },
}

// code blocks
// ```js
// code
// ```

const codeBlock = {
    order: SimpleMarkdown.defaultRules.codeBlock.order - 0.2,
    match: function(source, state, lookbehind) {
        return /^```([a-z0-9]*)\n([\s\S]*?)\n?```/.exec(source);
    },
    parse: function(capture, recurseParse, state) {
        return {
            type: 'codeBlock',
            language: capture[1],
            content: capture[2].trim(),
        };
    },
    html: function(node, recurseOutput, state) {
        try {
            let highlightedCode = ''
            if (node.language === '') {
                highlightedCode = node.content;
            }
            else {
                highlightedCode = hljs.highlight(node.language, node.content).value;
            }
            return `<pre><code class="hljs-codeblock language-${node.language}">${highlightedCode}</code></pre>`;
        }
        catch (error) {
            return `<pre><code class="hljs-codeblock language-${node.language}">${node.content}</code></pre>`;
        }
    },
}

// badly formatted code blocks - without language and code in the first or last line
// ```private void main() {
// code
// }```
const badlyFormattedCodeBlock = {
    order: SimpleMarkdown.defaultRules.codeBlock.order - 0.1,
    match: function(source, state, lookbehind) {
        return /^```([\s\S]*?\n[\s\S]*?)```/.exec(source);
    },
    parse: function(capture, recurseParse, state) {
        return {
            type: 'codeBlock',
            content: capture[1].trim(),
        };
    },
    html: function(node, recurseOutput, state) {
        try {
            const highlightedCode = hljs.highlight("txt", node.content).value;
            return `<pre><code class="hljs-codeblock">${highlightedCode}</code></pre>`;
        }
        catch (error) {
            return `<pre><code class="hljs-codeblock">${node.content}</code></pre>`;
        }
    },
}





export const rules = {
    array: SimpleMarkdown.defaultRules.array,
    customHeading: customHeading,
    // heading: SimpleMarkdown.defaultRules.heading,  // disabled because customHeading is used instead
    nptable: SimpleMarkdown.defaultRules.nptable,
    // lheading: SimpleMarkdown.defaultRules.lheading,
    hr: SimpleMarkdown.defaultRules.hr,
    codeBlock: codeBlock,
    badlyFormattedCodeBlock: badlyFormattedCodeBlock,
    // codeBlock: SimpleMarkdown.defaultRules.codeBlock,
    fence: SimpleMarkdown.defaultRules.fence,
    blockQuote: SimpleMarkdown.defaultRules.blockQuote,
    list: SimpleMarkdown.defaultRules.list,
    def: SimpleMarkdown.defaultRules.def,
    table: SimpleMarkdown.defaultRules.table,
    tableSeparator: SimpleMarkdown.defaultRules.tableSeparator,
    newline: SimpleMarkdown.defaultRules.newline,
    paragraph: SimpleMarkdown.defaultRules.paragraph,
    escape: SimpleMarkdown.defaultRules.escape,
    messageLink: messageLink,
    channelLink: channelLink,
    assetLink: assetLink,
    oldEmoji: oldEmoji,
    newEmoji: newEmoji,
    autolink: SimpleMarkdown.defaultRules.autolink,
    mailto: SimpleMarkdown.defaultRules.mailto,
    url: SimpleMarkdown.defaultRules.url,
    link: SimpleMarkdown.defaultRules.link,
    image: SimpleMarkdown.defaultRules.image,
    // reflink: SimpleMarkdown.defaultRules.reflink,
    refimage: SimpleMarkdown.defaultRules.refimage,
    em: SimpleMarkdown.defaultRules.em,
    strong: SimpleMarkdown.defaultRules.strong,
    u: SimpleMarkdown.defaultRules.u,
    del: SimpleMarkdown.defaultRules.del,
    inlineCode: SimpleMarkdown.defaultRules.inlineCode,
    br: SimpleMarkdown.defaultRules.br,
    timestamp: timestamp,
    newRole: newRole,
    mention: oldMention,
    newMention: newMention,
    newChannel: newChannel,
    highlightSearchTerms: highlightSearchTerms,
    twemoji: twemoji,
    textSpoiler: textSpoiler,
    text: SimpleMarkdown.defaultRules.text,
};

const parse = SimpleMarkdown.parserFor(rules);
var htmlOutput = SimpleMarkdown.outputFor(rules, 'html');




export function parseMarkdown(input: string, state: any) {
    let tree = parse(input, state);
    return {
        tree: tree,
        html: htmlOutput(tree)
    }
}