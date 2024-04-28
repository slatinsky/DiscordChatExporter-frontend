<script lang="ts">
    import { checkUrl } from "../../js/helpers";
    import type { Message } from "../../js/interfaces";
    import AuthorModal from "./AuthorModal.svelte";
    import MessageAuthorName from "./MessageAuthorName.svelte";
    import MessageMarkdown from "./MessageMarkdown.svelte";
    import { onUserRightClick } from "./messageRightClick";

    export let referencedMessage: Message
    export let authorModal: AuthorModal
</script>

{#if referencedMessage}
    <div class="referenced">
        <div class="referenced-arrow" />
        {#if referencedMessage.author}
            <img class="referenced-avatar" src={checkUrl(referencedMessage.author.avatar)} alt="avatar" on:click on:contextmenu|preventDefault={e=>onUserRightClick(e, referencedMessage.author)}  />
            <MessageAuthorName author={referencedMessage.author} on:click={() => authorModal.viewAuthor(referencedMessage.author)} />
            <div class="referenced-content">
                <MessageMarkdown content={referencedMessage.content[0].content.split("\n")[0]} />
            </div>
        {/if}
    </div>
{/if}

<style>
    .referenced {
        display: flex;
        gap: 2px;
        align-items: center;
    }

    .referenced-arrow {
        height: 14px;
        margin: 14px 0 4px 16px;
        border-left: 2px solid #4E5058;
        border-top: 2px solid #4E5058;
        border-radius: 8px 0 0 0;
        width: 35px;
    }

    .referenced-avatar {
        width: 16px;
        height: 16px;
        border-radius: 50%;
    }

    .referenced-content {
        overflow: hidden;
        text-overflow: ellipsis;
        max-height: 33px;

        margin-top: 1px;
        margin-left: 3px;

        color: #b5b6b8;
        font-size: 0.875rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis
    }
</style>