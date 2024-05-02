<script lang="ts">
    import { checkUrl } from "../../js/helpers";
    import type { Reaction } from "../../js/interfaces";
    import { currentUserId } from "../../js/stores/settingsStore.svelte";
    import ReactionsModal from "./ReactionsModal.svelte";

    export let reactions: Reaction[];

    let reactionsModal: ReactionsModal;
</script>


<ReactionsModal {reactions} bind:this={reactionsModal} />

<div class="message-reactions">
    {#each reactions as reaction}
        {@const emojiUsers = reaction?.users?.map(user => user._id) ?? []}
        <div class="message-reaction" class:me={emojiUsers.includes($currentUserId)} title=":{reaction.emoji.name}:" on:click={()=>reactionsModal.viewReactions(reaction)}>
            <img
                src={checkUrl(reaction.emoji?.image)}
                alt="Avatar"
                width="100%"
                height="100%"
            />
            <span class="message-reaction-count">{reaction.count}</span>
        </div>
    {/each}
</div>

<style>
    .message-reactions {
        display: flex;
        gap: 4px;
    }

    .message-reaction {
        margin-right: 4px;
        display: flex;
        margin: 5px 1px 1px 0;
        padding: 2px 6px;
        border: 1px solid transparent;
        border-radius: 8px;
        background-color: #2b2d31;
        align-items: center;
    }

    .message-reaction.me {
        border: 1px solid #5561E9;
        background-color: #34374F;
    }

    .message-reaction img {
        width: 16px;
        height: auto;
    }

    .message-reaction-count {
        margin-left: 0.35rem;
        font-size: 16px;
        font-weight: 600;
        margin-left: 6px;
        text-align: center;
        color: #B5BAC1;
    }

    .message-reaction:hover .message-reaction-count {
        color: #dcddde
    }
    .message-reaction.me .message-reaction-count {
        color: #DEE0FC;
    }
</style>