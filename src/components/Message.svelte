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
         class="chatlog__message-container {message.isPinned ? 'chatlog__message-container--pinned' : ''}"
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


<!--<div id="chatlog__message-container-@message.Id" class="chatlog__message-container @(message.IsPinned ? "-->
<!--     chatlog__message-container&#45;&#45;pinned" : null)" data-message-id="@message.Id">-->
<!--<div class="chatlog__message">-->
<!--    @{/* System notification */}-->
<!--    @if (message.Kind.IsSystemNotification())-->
<!--    {-->
<!--        // System notifications are grouped even if the message author is different.-->
<!--        // That's why we have to update the user values with the author of the current message.-->
<!--        userMember = Model.ExportContext.TryGetMember(message.Author.Id);-->
<!--        userColor = Model.ExportContext.TryGetUserColor(message.Author.Id);-->
<!--        userNick = message.Author.IsBot-->
<!--        ? message.Author.Name-->
<!--        : userMember?.Nick ?? message.Author.Name;-->

<!--        <div class="chatlog__message-aside">-->
<!--        <svg class="chatlog__system-notification-icon"><use href="#@message.Kind.ToString().ToDashCase().ToLowerInvariant()-icon"></use></svg>-->
<!--        </div>-->

<!--        <div class="chatlog__message-primary">-->
<!--        @{/* Author name */}-->
<!--        <span class="chatlog__system-notification-author" style="@(userColor is not null ? $"color: rgb({userColor.Value.R}, {userColor.Value.G}, {userColor.Value.B})" : null)" title="@message.Author.FullName" data-user-id="@message.Author.Id">@userNick</span>-->

<!--        @{/* System notification content */}-->
<!--        <span class="chatlog__system-notification-content">-->
<!--        @if (message.Kind == MessageKind.ChannelPinnedMessage && message.Reference is not null)-->
<!--            {-->
<!--        <span> pinned</span>-->
<!--        <a class="chatlog__system-notification-link" href="#chatlog__message-container-@message.Reference.MessageId"> a message</a>-->
<!--        <span> to this channel.</span>-->
<!--    }-->
<!--        else-->
<!--            {-->
<!--        <span>@message.Content.ToLowerInvariant()</span>-->
<!--    }-->
<!--        </span>-->

<!--        @{/* Timestamp */}-->
<!--        <span class="chatlog__system-notification-timestamp">-->
<!--        <a href="#chatlog__message-container-@message.Id">@FormatDate(message.Timestamp)</a>-->
<!--        </span>-->
<!--        </div>-->
<!--    }-->
<!--        // Regular message-->
<!--        else-->
<!--            {-->
<!--        <div class="chatlog__message-aside">-->
<!--        @if (isFirst)-->
<!--            {-->
<!--        // Reference symbol-->
<!--        if (message.Reference is not null)-->
<!--            {-->
<!--        <div class="chatlog__reference-symbol"></div>-->
<!--    }-->

<!--        // Avatar-->
<!--        <img class="chatlog__avatar" src="@await ResolveUrlAsync(message.Author.AvatarUrl)" alt="Avatar" loading="lazy">-->
<!--        }-->
<!--        else-->
<!--            {-->
<!--        <div class="chatlog__short-timestamp" title="@FormatDate(message.Timestamp)">@message.Timestamp.ToLocalString("t")</div>-->
<!--    }-->
<!--        </div>-->

<!--        <div class="chatlog__message-primary">-->
<!--        @if (isFirst)-->
<!--            {-->
<!--        // Reference-->
<!--        if (message.Reference is not null)-->
<!--            {-->
<!--        <div class="chatlog__reference">-->
<!--        @if (message.ReferencedMessage is not null)-->
<!--            {-->
<!--        <img class="chatlog__reference-avatar" src="@await ResolveUrlAsync(message.ReferencedMessage.Author.AvatarUrl)" alt="Avatar" loading="lazy">-->
<!--        <div class="chatlog__reference-author" style="@(referencedUserColor is not null ? $"color: rgb({referencedUserColor.Value.R}, {referencedUserColor.Value.G}, {referencedUserColor.Value.B})" : null)" title="@message.ReferencedMessage.Author.FullName">@referencedUserNick</div>-->
<!--        <div class="chatlog__reference-content">-->
<!--        <span class="chatlog__reference-link" onclick="scrollToMessage(event, '@message.ReferencedMessage.Id')">-->
<!--        @if (!string.IsNullOrWhiteSpace(message.ReferencedMessage.Content) && !message.ReferencedMessage.IsContentHidden())-->
<!--            {-->
<!--        &lt;!&ndash;wmm:ignore&ndash;&gt;@Raw(FormatEmbedMarkdown(message.ReferencedMessage.Content))&lt;!&ndash;/wmm:ignore&ndash;&gt;-->
<!--    }-->
<!--        else if (message.ReferencedMessage.Attachments.Any() || message.ReferencedMessage.Embeds.Any())-->
<!--            {-->
<!--        <em>Click to see attachment</em>-->
<!--        <span>🖼️</span>-->
<!--    }-->
<!--        else-->
<!--            {-->
<!--        <em>Click to see original message</em>-->
<!--    }-->
<!--        </span>-->

<!--        @if (message.ReferencedMessage.EditedTimestamp is not null)-->
<!--            {-->
<!--        <span class="chatlog__reference-edited-timestamp" title="@FormatDate(message.ReferencedMessage.EditedTimestamp.Value)">(edited)</span>-->
<!--    }-->
<!--        </div>-->
<!--    }-->
<!--        else-->
<!--            {-->
<!--        <div class="chatlog__reference-unknown">-->
<!--        Original message was deleted or could not be loaded.-->
<!--        </div>-->
<!--    }-->
<!--        </div>-->
<!--    }-->

<!--        // Header-->
<!--        <div class="chatlog__header">-->
<!--        @{/* Author name */}-->
<!--        <span class="chatlog__author" style="@(userColor is not null ? $"color: rgb({userColor.Value.R}, {userColor.Value.G}, {userColor.Value.B})" : null)" title="@message.Author.FullName" data-user-id="@message.Author.Id">@userNick</span>-->

<!--        @{/* Bot label */}-->
<!--        @if (message.Author.IsBot)-->
<!--            {-->
<!--        <span class="chatlog__bot-label">BOT</span>-->
<!--    }-->

<!--        @{/* Timestamp */}-->
<!--        <span class="chatlog__timestamp"><a href="#chatlog__message-container-@message.Id">@FormatDate(message.Timestamp)</a></span>-->
<!--        </div>-->
<!--    }-->

<!--        @{/* Content */}-->
<!--        @if ((!string.IsNullOrWhiteSpace(message.Content) && !message.IsContentHidden()) || message.EditedTimestamp is not null)-->
<!--            {-->
<!--        <div class="chatlog__content chatlog__markdown">-->
<!--        @{/* Text */}-->
<!--        @if (!string.IsNullOrWhiteSpace(message.Content) && !message.IsContentHidden())-->
<!--            {-->
<!--        <span class="chatlog__markdown-preserve">&lt;!&ndash;wmm:ignore&ndash;&gt;@Raw(FormatMarkdown(message.Content))&lt;!&ndash;/wmm:ignore&ndash;&gt;</span>-->
<!--    }-->

<!--        @{/* Edited timestamp */}-->
<!--        @if (message.EditedTimestamp is not null)-->
<!--            {-->
<!--        <span class="chatlog__edited-timestamp" title="@FormatDate(message.EditedTimestamp.Value)">(edited)</span>-->
<!--    }-->
<!--        </div>-->
<!--    }-->

<!--        @{/* Attachments */}-->
<!--        @foreach (var attachment in message.Attachments)-->
<!--            {-->
<!--        <div class="chatlog__attachment @(attachment.IsSpoiler ? "chatlog__attachment&#45;&#45;hidden" : null)" onclick="@(attachment.IsSpoiler ? "showSpoiler(event, this)" : null)">-->
<!--        @{/* Spoiler caption */}-->
<!--        @if (attachment.IsSpoiler)-->
<!--            {-->
<!--        <div class="chatlog__attachment-spoiler-caption">SPOILER</div>-->
<!--    }-->

<!--        @{/* Attachment preview */}-->
<!--        @if (attachment.IsImage)-->
<!--            {-->
<!--        <a href="@await ResolveUrlAsync(attachment.Url)">-->
<!--        <img class="chatlog__attachment-media" src="@await ResolveUrlAsync(attachment.Url)" alt="@(attachment.Description ?? "Image attachment")" title="Image: @attachment.FileName (@attachment.FileSize)" loading="lazy">-->
<!--        </a>-->
<!--        }-->
<!--        else if (attachment.IsVideo)-->
<!--            {-->
<!--        <video class="chatlog__attachment-media" controls>-->
<!--        <source src="@await ResolveUrlAsync(attachment.Url)" alt="@(attachment.Description ?? "Video attachment")" title="Video: @attachment.FileName (@attachment.FileSize)">-->
<!--        </video>-->
<!--        }-->
<!--        else if (attachment.IsAudio)-->
<!--            {-->
<!--        <audio class="chatlog__attachment-media" controls>-->
<!--        <source src="@await ResolveUrlAsync(attachment.Url)" alt="@(attachment.Description ?? "Audio attachment")" title="Audio: @attachment.FileName (@attachment.FileSize)">-->
<!--        </audio>-->
<!--        }-->
<!--        else-->
<!--            {-->
<!--        <div class="chatlog__attachment-generic">-->
<!--        <svg class="chatlog__attachment-generic-icon">-->
<!--        <use href="#attachment-icon"/>-->
<!--        </svg>-->
<!--        <div class="chatlog__attachment-generic-name">-->
<!--        <a href="@await ResolveUrlAsync(attachment.Url)">-->
<!--        @attachment.FileName-->
<!--        </a>-->
<!--        </div>-->
<!--        <div class="chatlog__attachment-generic-size">-->
<!--        @attachment.FileSize-->
<!--        </div>-->
<!--        </div>-->
<!--    }-->
<!--        </div>-->
<!--    }-->

<!--        @{/* Embeds */}-->
<!--        @foreach (var embed in message.Embeds)-->
<!--            {-->
<!--        // Spotify embed-->
<!--        if (embed.TryGetSpotifyTrack() is { } spotifyTrackEmbed)-->
<!--            {-->
<!--        <div class="chatlog__embed">-->
<!--        <div class="chatlog__embed-spotify-container">-->
<!--        <iframe class="chatlog__embed-spotify" src="@spotifyTrackEmbed.Url" width="400" height="80" allowtransparency="true" allow="encrypted-media"></iframe>-->
<!--        </div>-->
<!--        </div>-->
<!--    }-->
<!--        // YouTube embed-->
<!--        else if (embed.TryGetYouTubeVideo() is { } youTubeVideoEmbed)-->
<!--            {-->
<!--        <div class="chatlog__embed">-->
<!--        @{/* Color pill */}-->
<!--        @if (embed.Color is not null)-->
<!--            {-->
<!--        <div class="chatlog__embed-color-pill" style="background-color: rgba(@embed.Color.Value.R, @embed.Color.Value.G, @embed.Color.Value.B, @embed.Color.Value.A)"></div>-->
<!--    }-->
<!--        else-->
<!--            {-->
<!--        <div class="chatlog__embed-color-pill chatlog__embed-color-pill&#45;&#45;default"></div>-->
<!--    }-->

<!--        <div class="chatlog__embed-content-container">-->
<!--        <div class="chatlog__embed-content">-->
<!--        <div class="chatlog__embed-text">-->
<!--        @{/* Embed author */}-->
<!--        @if (embed.Author is not null)-->
<!--            {-->
<!--        <div class="chatlog__embed-author-container">-->
<!--        @if (!string.IsNullOrWhiteSpace(embed.Author.IconUrl))-->
<!--            {-->
<!--        <img class="chatlog__embed-author-icon" src="@await ResolveUrlAsync(embed.Author.IconProxyUrl ?? embed.Author.IconUrl)" alt="Author icon" loading="lazy" onerror="this.style.visibility='hidden'">-->
<!--        }-->

<!--        @if (!string.IsNullOrWhiteSpace(embed.Author.Name))-->
<!--            {-->
<!--        if (!string.IsNullOrWhiteSpace(embed.Author.Url))-->
<!--            {-->
<!--        <a class="chatlog__embed-author-link" href="@embed.Author.Url">-->
<!--        <div class="chatlog__embed-author">@embed.Author.Name</div>-->
<!--        </a>-->
<!--    }-->
<!--        else-->
<!--            {-->
<!--        <div class="chatlog__embed-author">@embed.Author.Name</div>-->
<!--    }-->
<!--    }-->
<!--        </div>-->
<!--    }-->

<!--        @{/* Embed title */}-->
<!--        @if (!string.IsNullOrWhiteSpace(embed.Title))-->
<!--            {-->
<!--        <div class="chatlog__embed-title">-->
<!--        @if (!string.IsNullOrWhiteSpace(embed.Url))-->
<!--            {-->
<!--        <a class="chatlog__embed-title-link" href="@embed.Url">-->
<!--        <div class="chatlog__markdown chatlog__markdown-preserve">&lt;!&ndash;wmm:ignore&ndash;&gt;@Raw(FormatEmbedMarkdown(embed.Title))&lt;!&ndash;/wmm:ignore&ndash;&gt;</div>-->
<!--        </a>-->
<!--    }-->
<!--        else-->
<!--            {-->
<!--        <div class="chatlog__markdown chatlog__markdown-preserve">&lt;!&ndash;wmm:ignore&ndash;&gt;@Raw(FormatEmbedMarkdown(embed.Title))&lt;!&ndash;/wmm:ignore&ndash;&gt;</div>-->
<!--    }-->
<!--        </div>-->
<!--    }-->

<!--        @{/* Video player */}-->
<!--        <div class="chatlog__embed-youtube-container">-->
<!--        <iframe class="chatlog__embed-youtube" src="@youTubeVideoEmbed.Url" width="400" height="225"></iframe>-->
<!--        </div>-->
<!--        </div>-->
<!--        </div>-->
<!--        </div>-->
<!--        </div>-->
<!--    }-->
<!--        // Generic image embed-->
<!--        else if (embed.Kind == EmbedKind.Image && !string.IsNullOrWhiteSpace(embed.Url))-->
<!--            {-->
<!--        <div class="chatlog__embed">-->
<!--        <a href="@await ResolveUrlAsync(embed.Url)">-->
<!--        <img class="chatlog__embed-generic-image" src="@await ResolveUrlAsync(embed.Url)" alt="Embedded image" loading="lazy">-->
<!--        </a>-->
<!--        </div>-->
<!--        }-->
<!--        // Generic gifv embed-->
<!--        else if (embed.Kind == EmbedKind.Gifv && !string.IsNullOrWhiteSpace(embed.Video?.Url))-->
<!--            {-->
<!--        <div class="chatlog__embed">-->
<!--        <video class="chatlog__embed-generic-gifv" loop width="@embed.Video.Width" height="@embed.Video.Height" onmouseover="this.play()" onmouseout="this.pause()">-->
<!--        <source src="@await ResolveUrlAsync(embed.Video.ProxyUrl ?? embed.Video.Url)" alt="Embedded video">-->
<!--        </video>-->
<!--        </div>-->
<!--        }-->
<!--        // Rich embed-->
<!--        else-->
<!--            {-->
<!--        <div class="chatlog__embed">-->
<!--        @{/* Color pill */}-->
<!--        @if (embed.Color is not null)-->
<!--            {-->
<!--        <div class="chatlog__embed-color-pill" style="background-color: rgba(@embed.Color.Value.R, @embed.Color.Value.G, @embed.Color.Value.B, @embed.Color.Value.A)"></div>-->
<!--    }-->
<!--        else-->
<!--            {-->
<!--        <div class="chatlog__embed-color-pill chatlog__embed-color-pill&#45;&#45;default"></div>-->
<!--    }-->

<!--        <div class="chatlog__embed-content-container">-->
<!--        <div class="chatlog__embed-content">-->
<!--        <div class="chatlog__embed-text">-->
<!--        @{/* Embed author */}-->
<!--        @if (embed.Author is not null)-->
<!--            {-->
<!--        <div class="chatlog__embed-author-container">-->
<!--        @if (!string.IsNullOrWhiteSpace(embed.Author.IconUrl))-->
<!--            {-->
<!--        <img class="chatlog__embed-author-icon" src="@await ResolveUrlAsync(embed.Author.IconProxyUrl ?? embed.Author.IconUrl)" alt="Author icon" loading="lazy" onerror="this.style.visibility='hidden'">-->
<!--        }-->

<!--        @if (!string.IsNullOrWhiteSpace(embed.Author.Name))-->
<!--            {-->
<!--        if (!string.IsNullOrWhiteSpace(embed.Author.Url))-->
<!--            {-->
<!--        <a class="chatlog__embed-author-link" href="@embed.Author.Url">-->
<!--        <div class="chatlog__embed-author">@embed.Author.Name</div>-->
<!--        </a>-->
<!--    }-->
<!--        else-->
<!--            {-->
<!--        <div class="chatlog__embed-author">@embed.Author.Name</div>-->
<!--    }-->
<!--    }-->
<!--        </div>-->
<!--    }-->

<!--        @{/* Embed title */}-->
<!--        @if (!string.IsNullOrWhiteSpace(embed.Title))-->
<!--            {-->
<!--        <div class="chatlog__embed-title">-->
<!--        @if (!string.IsNullOrWhiteSpace(embed.Url))-->
<!--            {-->
<!--        <a class="chatlog__embed-title-link" href="@embed.Url">-->
<!--        <div class="chatlog__markdown chatlog__markdown-preserve">&lt;!&ndash;wmm:ignore&ndash;&gt;@Raw(FormatEmbedMarkdown(embed.Title))&lt;!&ndash;/wmm:ignore&ndash;&gt;</div>-->
<!--        </a>-->
<!--    }-->
<!--        else-->
<!--            {-->
<!--        <div class="chatlog__markdown chatlog__markdown-preserve">&lt;!&ndash;wmm:ignore&ndash;&gt;@Raw(FormatEmbedMarkdown(embed.Title))&lt;!&ndash;/wmm:ignore&ndash;&gt;</div>-->
<!--    }-->
<!--        </div>-->
<!--    }-->

<!--        @{/* Embed description */}-->
<!--        @if (!string.IsNullOrWhiteSpace(embed.Description))-->
<!--            {-->
<!--        <div class="chatlog__embed-description">-->
<!--        <div class="chatlog__markdown chatlog__markdown-preserve">&lt;!&ndash;wmm:ignore&ndash;&gt;@Raw(FormatEmbedMarkdown(embed.Description))&lt;!&ndash;/wmm:ignore&ndash;&gt;</div>-->
<!--        </div>-->
<!--    }-->

<!--        @{/* Embed fields */}-->
<!--        @if (embed.Fields.Any())-->
<!--            {-->
<!--        <div class="chatlog__embed-fields">-->
<!--        @foreach (var field in embed.Fields)-->
<!--            {-->
<!--        <div class="chatlog__embed-field @(field.IsInline ? "chatlog__embed-field&#45;&#45;inline" : null)">-->
<!--        @if (!string.IsNullOrWhiteSpace(field.Name))-->
<!--            {-->
<!--        <div class="chatlog__embed-field-name">-->
<!--        <div class="chatlog__markdown chatlog__markdown-preserve">&lt;!&ndash;wmm:ignore&ndash;&gt;@Raw(FormatEmbedMarkdown(field.Name))&lt;!&ndash;/wmm:ignore&ndash;&gt;</div>-->
<!--        </div>-->
<!--    }-->

<!--        @if (!string.IsNullOrWhiteSpace(field.Value))-->
<!--            {-->
<!--        <div class="chatlog__embed-field-value">-->
<!--        <div class="chatlog__markdown chatlog__markdown-preserve">&lt;!&ndash;wmm:ignore&ndash;&gt;@Raw(FormatEmbedMarkdown(field.Value))&lt;!&ndash;/wmm:ignore&ndash;&gt;</div>-->
<!--        </div>-->
<!--    }-->
<!--        </div>-->
<!--    }-->
<!--        </div>-->
<!--    }-->
<!--        </div>-->

<!--        @{/* Embed content */}-->
<!--        @if (embed.Thumbnail is not null && !string.IsNullOrWhiteSpace(embed.Thumbnail.Url))-->
<!--            {-->
<!--        <div class="chatlog__embed-thumbnail-container">-->
<!--        <a class="chatlog__embed-thumbnail-link" href="@await ResolveUrlAsync(embed.Thumbnail.ProxyUrl ?? embed.Thumbnail.Url)">-->
<!--        <img class="chatlog__embed-thumbnail" src="@await ResolveUrlAsync(embed.Thumbnail.ProxyUrl ?? embed.Thumbnail.Url)" alt="Thumbnail" loading="lazy">-->
<!--        </a>-->
<!--        </div>-->
<!--        }-->
<!--        </div>-->

<!--        @{/* Embed images */}-->
<!--        @if (embed.Images.Any())-->
<!--            {-->
<!--        <div class="chatlog__embed-images @(embed.Images.Count == 1 ? "chatlog__embed-images&#45;&#45;single" : null)">-->
<!--        @foreach (var image in embed.Images)-->
<!--            {-->
<!--        if (!string.IsNullOrWhiteSpace(image.Url))-->
<!--            {-->
<!--        <div class="chatlog__embed-image-container">-->
<!--        <a class="chatlog__embed-image-link" href="@await ResolveUrlAsync(image.ProxyUrl ?? image.Url)">-->
<!--        <img class="chatlog__embed-image" src="@await ResolveUrlAsync(image.ProxyUrl ?? image.Url)" alt="Image" loading="lazy">-->
<!--        </a>-->
<!--        </div>-->
<!--        }-->
<!--        }-->
<!--        </div>-->
<!--    }-->

<!--        @{/* Embed footer & icon */}-->
<!--        @if (embed.Footer is not null || embed.Timestamp is not null)-->
<!--            {-->
<!--        <div class="chatlog__embed-footer">-->
<!--        @{/* Footer icon */}-->
<!--        @if (!string.IsNullOrWhiteSpace(embed.Footer?.IconUrl))-->
<!--            {-->
<!--        <img class="chatlog__embed-footer-icon" src="@await ResolveUrlAsync(embed.Footer.IconProxyUrl ?? embed.Footer.IconUrl)" alt="Footer icon" loading="lazy">-->
<!--        }-->

<!--        <span class="chatlog__embed-footer-text">-->
<!--        @{/* Footer text */}-->
<!--        @if (!string.IsNullOrWhiteSpace(embed.Footer?.Text))-->
<!--            {-->
<!--        @embed.Footer.Text-->
<!--    }-->

<!--        @if (!string.IsNullOrWhiteSpace(embed.Footer?.Text) && embed.Timestamp is not null)-->
<!--            {-->
<!--        @(" • ")-->
<!--    }-->

<!--        @{/* Embed timestamp */}-->
<!--        @if (embed.Timestamp is not null)-->
<!--            {-->
<!--        @FormatDate(embed.Timestamp.Value)-->
<!--    }-->
<!--        </span>-->
<!--        </div>-->
<!--    }-->
<!--        </div>-->
<!--        </div>-->
<!--    }-->
<!--    }-->

<!--        @{/* Stickers */}-->
<!--        @foreach (var sticker in message.Stickers)-->
<!--            {-->
<!--        <div class="chatlog__sticker" title="@sticker.Name">-->
<!--        @if (sticker.Format is StickerFormat.Png or StickerFormat.PngAnimated)-->
<!--            {-->
<!--        <img class="chatlog__sticker&#45;&#45;media" src="@await ResolveUrlAsync(sticker.SourceUrl)" alt="Sticker">-->
<!--        }-->
<!--        else if (sticker.Format == StickerFormat.Lottie)-->
<!--            {-->
<!--        <div class="chatlog__sticker&#45;&#45;media" data-source="@await ResolveUrlAsync(sticker.SourceUrl)"></div>-->
<!--    }-->
<!--        </div>-->
<!--    }-->

<!--        @{/* Message reactions */}-->
<!--        @if (message.Reactions.Any())-->
<!--            {-->
<!--        <div class="chatlog__reactions">-->
<!--        @foreach (var reaction in message.Reactions)-->
<!--            {-->
<!--        <div class="chatlog__reaction" title="@reaction.Emoji.Code">-->
<!--        <img class="chatlog__emoji chatlog__emoji&#45;&#45;small" alt="@reaction.Emoji.Name" src="@await ResolveUrlAsync(reaction.Emoji.ImageUrl)" loading="lazy">-->
<!--        <span class="chatlog__reaction-count">@reaction.Count</span>-->
<!--        </div>-->
<!--        }-->
<!--        </div>-->
<!--    }-->
<!--        </div>-->
<!--    }-->
<!--        </div>-->
<!--        </div>-->