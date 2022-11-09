<script>
    export let message = null
    export let authors = null

    message.author = authors[message.authorId]


    function human_timestamp_format(timestamp) {
        return timestamp.replace('T', ' ').split('.')[0]
    }

    function full_name(author) {
        return author.name + '#' + author.discriminator
    }

    // recreated from https://github.com/Tyrrrz/DiscordChatExporter/blob/dabed24c16c925d4f9ec2a069bf443653372e6cc/DiscordChatExporter.Core/Exporting/Writers/Html/MessageGroupTemplate.cshtml#L114
</script>

<div class=chatlog__message-group>
    <div id=chatlog__message-container-{message.id}
         class="chatlog__message-container"
         class:chatlog__message-container--pinned={message.isPinned}
         data-message-id={message.id}>
        <div class=chatlog__message>
            <!--            TODO: system notification-->
            <!--            Regular message-->
            <div class=chatlog__message-aside>
                {#if message.referencedMessage}
                    <div class=chatlog__reference-symbol></div>
                {/if}

                <img class=chatlog__avatar
                     src={message.author.avatarUrl}
                     alt=Avatar loading=lazy>
            </div>

            <div class=chatlog__message-primary>
                {#if message.referencedMessage}
                    <div class="chatlog__reference">
                        <img class="chatlog__reference-avatar"
                             src="{message.referencedMessage.author.avatarUrl}" alt="Avatar"
                             loading="lazy">
                        <div class="chatlog__reference-author" style="color: {message.referencedMessage.author.color}"
                             title="{full_name(message.referencedMessage.author)}">{message.referencedMessage.author.name}</div>
                        <div class=chatlog__reference-content><span class=chatlog__reference-link
                                                                    onclick="scrollToMessage(event,message.reference.messageId)">{message.referencedMessage.content}</span>
                        </div>
                    </div>
                {/if}
                <div class=chatlog__header><span class=chatlog__author title=NightSlayer907#4484
                                                 data-user-id={message.author.id}>{message.author.nickname}</span> <span
                        class=chatlog__timestamp><a
                        href=#chatlog__message-container-{message.id}>{human_timestamp_format(message.timestamp)}</a></span>
                </div>
                <div class="chatlog__content chatlog__markdown">

                    <span
                            class=chatlog__markdown-preserve>{message.content}</span>
                    {#if message.timestampEdited != null}
                        <span class=chatlog__edited-timestamp title="{message.timestampEdited}">(edited)</span>
                    {/if}
                </div>
                {#each message.attachments as attachment}
                    <div class=chatlog__attachment><a
                            href={attachment.url}>
                        <img class=chatlog__attachment-media
                             src={attachment.url}
                             alt="Attachment" title="Image: {attachment.fileName} ({attachment.fileSizeBytes} KB)"
                             loading=lazy> </a></div>
                {/each}
                {#each message.embeds as embed}
                    <div class=chatlog__embed><a
                            href={embed.url}>
                        <img class=chatlog__embed-generic-image
                             src={embed.thumbnail.url}
                             alt="Embedded image" loading=lazy> </a></div>
                {/each}
                <!--                TODO: stickers-->
                <!--                REACTIONS-->
                <div class=chatlog__reactions>
                    {#each message.reactions as reaction}
                        <div class=chatlog__reaction title={reaction.emoji.name}><img
                                class="chatlog__emoji chatlog__emoji--small"
                                alt=🍰
                                src={reaction.emoji.imageUrl}
                                loading=lazy> <span class=chatlog__reaction-count>{reaction.count}</span></div>
                    {/each}
                </div>
            </div>
        </div>
    </div>
</div>