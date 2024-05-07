<script lang="ts">
    import type { Author, Embed, Message } from "../../js/interfaces";
    import { channelOrThreadIdToName, getGuildState } from "../../js/stores/guildState.svelte";
    import IconAutomodShield from "../icons/IconAutomodShield.svelte";
    import { getViewUserState } from "../viewuser/viewUserState.svelte";
    import MessageAuthorName from "./MessageAuthorName.svelte";
    import MessageAvatar from "./MessageAvatar.svelte";
    import MessageMarkdown from "./MessageMarkdown.svelte";
    import MessageReactions from "./MessageReactions.svelte";
    import MessageTimestamp from "./MessageTimestamp.svelte";

    interface MyProps {
        message: Message;
        messageState: any
    }
    let { message, messageState}: MyProps = $props();
    const viewUserState = getViewUserState()


    const automodAuthorMock: Author = {
        _id: "automod",
        name: "AutoMod",
        nickname: "AutoMod",
        color: "#979ff4",
        isBot: true,
        avatar: {
            _id: "automod-avatar",
            originalPath: "../favicon.png",
            localPath: "../favicon.png",
            remotePath: "../favicon.png",
            path: "../favicon.png",
            extension: "png",
            type: "image",
            width: 3203,
            height: 2493,
            sizeBytes: 289310,
            filenameWithHash: "favicon.png",
            filenameWithoutHash: "favicon.png",
            colorDominant: null,
            colorPalette: null,
        },
        roles: []
    }

    const automodValues = $derived.by(()=> {
        const retObj: any = {
            messageContent: "",
            keyword: "",
            rule_name: "",
            timeout_duration: "",
            channel_id: "",
        }
        if (!message.embeds || message.embeds.length == 0) {
            return retObj
        }
        const embed: Embed = message.embeds[0]
        retObj.messageContent = embed.description

        // loop embed fields and add to retObj
        if (embed.fields) {
            for (let field of embed.fields) {
                retObj[field.name] = field.value
            }
        }

        retObj.channel_id = "0".repeat(24 - retObj.channel_id.length) + retObj.channel_id

        return retObj
    })
    const channelName: string | null = $derived.by(()=>channelOrThreadIdToName(automodValues.channel_id))

    const guildState = getGuildState()

    async function setChannel() {
        await guildState.comboSetGuildChannel(message.guildId, automodValues.channel_id)
        await guildState.pushState()
    }
</script>

<div class="wrapper">
    <div class="avatar-row">
        <MessageAvatar author={automodAuthorMock} messageState={messageState} />
        <div style="width: 100%;">
            <div class="authorline"><MessageAuthorName author={automodAuthorMock} /> has blocked a message in <a class="message-mention" onclick={setChannel} href="javascript:void(0)"><svg style="width: 1rem;height: 1rem;vertical-align: middle;margin-bottom: .2rem;margin-right:4px" width="24" height="24" viewBox="0 0 24 24" role="img"><path fill="currentColor" fill-rule="evenodd" clip-rule="evenodd" d="M5.88657 21C5.57547 21 5.3399 20.7189 5.39427 20.4126L6.00001 17H2.59511C2.28449 17 2.04905 16.7198 2.10259 16.4138L2.27759 15.4138C2.31946 15.1746 2.52722 15 2.77011 15H6.35001L7.41001 9H4.00511C3.69449 9 3.45905 8.71977 3.51259 8.41381L3.68759 7.41381C3.72946 7.17456 3.93722 7 4.18011 7H7.76001L8.39677 3.41262C8.43914 3.17391 8.64664 3 8.88907 3H9.87344C10.1845 3 10.4201 3.28107 10.3657 3.58738L9.76001 7H15.76L16.3968 3.41262C16.4391 3.17391 16.6466 3 16.8891 3H17.8734C18.1845 3 18.4201 3.28107 18.3657 3.58738L17.76 7H21.1649C21.4755 7 21.711 7.28023 21.6574 7.58619L21.4824 8.58619C21.4406 8.82544 21.2328 9 20.9899 9H17.41L16.35 15H19.7549C20.0655 15 20.301 15.2802 20.2474 15.5862L20.0724 16.5862C20.0306 16.8254 19.8228 17 19.5799 17H16L15.3632 20.5874C15.3209 20.8261 15.1134 21 14.8709 21H13.8866C13.5755 21 13.3399 20.7189 13.3943 20.4126L14 17H8.00001L7.36325 20.5874C7.32088 20.8261 7.11337 21 6.87094 21H5.88657ZM9.41045 9L8.35045 15H14.3504L15.4104 9H9.41045Z"></path></svg> {channelName ?? "channel"}</a> <MessageTimestamp channelOrThreadId={message.channelId} timestamp={message.timestamp} messageId={message._id} /></div>
            <div class="content">
                <div class="blocker-message">
                    <div class="avatar-row">
                        <MessageAvatar author={message.author} on:click={() => viewUserState.setUser(message.author)} messageState={messageState} />
                        <div style="width: 100%;">
                            <div class="authorline"><MessageAuthorName author={message.author} on:click={() => viewUserState.setUser(message.author)} /> <MessageTimestamp channelOrThreadId={message.channelId} timestamp={message.timestamp} messageId={message._id} /></div>
                            <div style="width: 100%;">
                                <MessageMarkdown content={automodValues.messageContent} />
                                <div class="rule-row">
                                    <div>Keyword: {automodValues.keyword}</div>
                                    <div class="separator"></div>
                                    <div>Rule: {automodValues.rule_name}</div>
                                    <div class="separator"></div>
                                    <div>Time-out: {automodValues.timeout_duration} secs</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="actions">
                    <IconAutomodShield />
                    <a>Actions</a>
                    <div class="separator"></div>
                    <a href="https://github.com/slatinsky/DiscordChatExporter-frontend/issues" target="_blank">Report Issues</a>
                </div>
            </div>

            {#if message.reactions}
                <MessageReactions reactions={message.reactions} />
            {/if}
        </div>
    </div>
</div>


<style>
    .avatar-row {
        display: grid;
        gap: 15px;
        grid-template-columns: 40px 1fr;
        width: 100%;

        .authorline {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 5px;
            margin-bottom: 2px;
        }
    }

    .content {
        max-width: 550px;
        width: 100%;
    }

    .blocker-message {
        border-top-left-radius:  8px;
        border-top-right-radius: 8px;
        background-color: #2B2D31;
        padding: 15px;
        margin-top: 4px;
    }

    .rule-row {
        display: flex;
        flex-direction: row;
        color: #969ba4;
        font-size: 12px;
        font-weight: 500;
        align-items: center;

        .separator {
            width: 5px;
            height: 5px;
            background-color: #3c3d44;
            border-radius: 50%;
            margin: 0 8px;
        }
    }

    .actions {
        border-bottom-left-radius:  8px;
        border-bottom-right-radius: 8px;
        background-color: #1e1f22;
        padding: 10px 18px;
        display: flex;
        align-items: center;
        color: #53a8f9;
        font-size: 12px;

        a {
            color: #53a8f9;
            display: block;
            margin: 0 5px;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }

        .separator {
            width: 4px;
            height: 4px;
            background-color: #36363c;
            border-radius: 50%;
            margin: 0 3px;
        }
    }







</style>