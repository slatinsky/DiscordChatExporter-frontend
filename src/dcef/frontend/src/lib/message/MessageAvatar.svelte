<script lang="ts">
    import { checkUrl } from "../../js/helpers";
    import type { Author } from "../../js/interfaces";
    import { onUserRightClick } from "./messageRightClick";

    export let author: Author
    export let messageState
</script>

{#if author}
    <img class="avatar" src={checkUrl(author.avatar)} alt="avatar" on:click on:contextmenu|preventDefault={e=>onUserRightClick(e, author)}  />
{/if}

<style>
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
    }
</style>