<script lang="ts">
    import { selectedThreadId } from "../../js/stores/guildStore";
    import IconThread from "../icons/IconThread.svelte";
    import IconThreadMiddle from "../icons/IconThreadMiddle.svelte";

    export let thread
    export let isLast

    function selectThread() {
        $selectedThreadId = thread._id
    }
</script>

<div class="thread" class:selected={thread._id == $selectedThreadId} on:click={selectThread}>
    <div class="thread-icon">
        {#if isLast}
            <IconThread />
        {:else}
            <IconThreadMiddle />
        {/if}
    </div>
    <div class="thread-name">{thread.name}</div>
</div>


<style>
    .thread {
        display: flex;
        height: 17px;
        margin: 0px 15px 0px 30px;
        font-size: small;
        align-items: flex-start;
        text-decoration: none;
        overflow: hidden;
        cursor: pointer;
    }
    .thread:hover {
        color: white;
    }

    .thread-icon {
        color: #80848E;
        overflow: visible;
    }

    .thread-name {
        padding-left: 7px;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        color: #80848E;
    }
    .selected .thread-name {
        color: white;
    }
</style>