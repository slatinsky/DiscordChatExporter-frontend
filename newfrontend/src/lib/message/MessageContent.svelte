<script lang="ts">
    import Message from "./Message.svelte";
    import MessageMarkdown from "./MessageMarkdown.svelte";

    export let message: Message[]
</script>

<MessageMarkdown content={message.content[0].content} emotes={message?.emotes || []} mentions={message?.mentions || []} roles={message?.roles || []} channels={message?.channels || []} />
{#if message.timestampEdited != null}
    <span class="edited-or-deleted" title={message.timestampEdited}
        >(edited)</span
    >
{/if}
{#if message.isDeleted}
    <span class="edited-or-deleted">(deleted)</span>
{/if}

<style>
    .edited-or-deleted {
        margin-left: 0.15rem;
        color: #a3a6aa;
        font-size: 0.75rem;
        font-weight: 500
    }
</style>