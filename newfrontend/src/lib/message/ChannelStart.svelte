<script lang="ts">
    import IconChannel from "../icons/IconChannel.svelte";
    import IconThread from "../icons/IconThread.svelte";

    export let isThread: boolean;
    export let channelName: string;
</script>

{#if isThread}
    <div class="wrapper">
        <div class="thread-icon">
            <IconThread width={30}/>
        </div>
        <div class="title">{channelName}!</div>
        <!-- TODO: find out who created the thread -->
        <div class="subtitle">Started by <span class="subtitle-person">Someone</span></div>
    </div>
{:else}
    <div class="wrapper">
        <div class="channel-icon">
            <IconChannel width={42}/>
        </div>
        <div class="title">Welcome to #{channelName}!</div>
        <div class="subtitle">This is the start of the #{channelName} channel. </div>
    </div>
{/if}


<style>
    .wrapper {
        /*can't use margin-top here - it is set by the parent to align the messages to the bottom */
        margin-left: 16px;
        margin-right: 16px;
        margin-bottom: 16px;
    }
    .channel-icon {
        background-color: #41434A;
        border-radius: 50%;
        width: 68px;
        height: 68px;
        display: grid;
        place-items: center;
        margin-top: 32px;
    }
    .thread-icon {
        background-color: #41434A;
        border-radius: 50%;
        width: 64px;
        height: 64px;
        display: grid;
        place-items: center;
        margin-top: 16px;
    }
    .title {
        font-size: 32px;
        font-weight: 700;
        color: #F2F3F5;
        margin: 8px 0;
    }
    .subtitle {
        color: #B5BAC1;
        font-size: 16px;

        .subtitle-person {
            color: #E6F3F5;
            font-weight: 600;
        }
    }
</style>