<script lang="ts">
    import type { Author } from "../../js/interfaces";
    import { nameRenderer } from "../../js/stores/settingsStore";
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

<style>
    .username {
        cursor: pointer;
    }
    .hover-underline:hover {
        text-decoration: underline;
    }
</style>