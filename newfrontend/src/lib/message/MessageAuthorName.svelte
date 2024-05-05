<script lang="ts">
    import type { Author } from "../../js/interfaces";
    import { nameRenderer } from "../../js/stores/settingsStore.svelte";
    import { onUserRightClick } from "./messageRightClick";

    export let author: Author


    function full_name(author: Author) {
        return author.name
	}
	function nickname_only(author: Author) {
		return author?.nickname ?? full_name(author);
	}
</script>


<button class="username {$$props.class}" title={nickname_only(author)} data-user-id={author.id} on:click on:contextmenu|preventDefault={e=>onUserRightClick(e, author)}>
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

{#if author?.isBot}
    <span class="tag-bot">APP</span>
{/if}

<style>
    .username {
        cursor: pointer;
        font-weight: 500;
    }
    .hover-underline:hover {
        text-decoration: underline;
    }

    .tag-bot {
        position: relative;
        top: -0.1rem;
        margin-left: 0.3rem;
        padding: 0.05rem 0.3rem;
        border-radius: 3px;
        background-color: #5865F2;
        color: #ffffff;
        font-size: 0.625rem;
        font-weight: 500;
        line-height: 1.3;
    }
</style>