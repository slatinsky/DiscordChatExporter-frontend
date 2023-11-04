<script lang="ts">
	import type { Author } from "src/js/interfaces";
	import { nameRenderer } from "../settings/settingsStore";

    export let author: Author;

    // duplicated function from NewMessage.svelte
    function full_name(author) {
        return author.name
	}
    // duplicated function from NewMessage.svelte
	function nickname_only(author) {
		return author?.nickname ?? full_name(author);
	}
</script>


<span on:click class="{$$props.class}" title={nickname_only(author)} data-user-id={author.id}>
    {#if $nameRenderer === 'handle' }
        <span style="color:{author.color}">{full_name(author)}</span>
    {:else if $nameRenderer === 'nickname' }
        <span style="color:{author.color}">{nickname_only(author)}</span>
    {:else if $nameRenderer === 'both'}
        <span style="color:{author.color}">{nickname_only(author)}</span>
        {#if nickname_only(author) !== full_name(author) }
            <span style="color:#949BA4"> ({full_name(author)})</span>
        {/if}
    {/if}
</span>

<style>
    .chatlog__author,
	.chatlog__system-notification-author,
	.chatlog__avatar {
		cursor: pointer;
	}
</style>