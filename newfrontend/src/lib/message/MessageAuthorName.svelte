<script lang="ts">
    import type { Author } from "../../js/interfaces";
    import { nameRenderer } from "../../js/stores/settingsStore.svelte";
    import Icon from "../icons/Icon.svelte";
    import { onUserRightClick } from "./messageRightClick";

    interface MyProps {
        author: Author
        messageState?: any
    }
    let { author, messageState}: MyProps = $props();

    function full_name(author: Author) {
        return author.name
	}
	function nickname_only(author: Author) {
		return author?.nickname ?? full_name(author);
	}

    let tag = $derived.by(() => {
        if (messageState && messageState.messageIsFromDifferentGuild) {
            return "SERVER"
        }
        else if (author?._id === "automod" || author.name === "discord") {
            return "SYSTEM"
        } else if (author?.isBot) {
            return "BOT"
        }
        return null
    })
</script>


<button class="username" class:verified={tag === "SYSTEM"} title={nickname_only(author)} data-user-id={author._id} on:click on:contextmenu|preventDefault={e=>onUserRightClick(e, author)}>
    {#if $nameRenderer === 'handle' }
        <span class="hover-underline" style="color:{author.color}">{full_name(author)}</span>
    {:else if $nameRenderer === 'nickname' }
        <span class="hover-underline" style="color:{author.color}">{nickname_only(author)}</span>
    {:else if $nameRenderer === 'both'}
        <span class="hover-underline" style="color:{author.color}">{nickname_only(author)}</span>
        {#if nickname_only(author) !== full_name(author) }
            <span style="color:#949BA4"> ({full_name(author)})</span>
        {/if}
    {/if}
</button>

{#if tag}
    <span class="tag-bot">
        {#if tag === "SYSTEM"}
            <div class="tick">
                <Icon name="other/verified" width={16} />
            </div>
        {/if}
        {tag}
    </span>
{/if}

<style>
    .username {
        cursor: pointer;
        font-weight: 500;
        &.verified {
            font-weight: 600;
        }
    }
    .hover-underline:hover {
        text-decoration: underline;
    }

    .tag-bot {
        position: relative;
        top: -0.1rem;
        margin-left: 0.3rem;
        padding: 0 4px;
        border-radius: 3px;
        background-color: #5865F2;
        color: #ffffff;
        font-size: 0.625rem;
        font-weight: 500;
        line-height: 1.3;

        display: inline-flex;
        align-items: center;
        max-height: 15px;

        .tick {
            display: grid;
            place-items: center;
            margin-left: -4px;
        }
    }
</style>