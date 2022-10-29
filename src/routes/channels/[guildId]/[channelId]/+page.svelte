<script>
	import { onMount } from "svelte";

    // import Preamble from "../../../components/Preamble.svelte";
	import Messages from "./Messages.svelte";
	import WatchHash from "./WatchHash.svelte";

    export let data;
    // console.log('data3', data);


    onMount(() => {

	});

    let mainChatlog

</script>

<svelte:head>
    <title>{data.guild.channels[data.channelId]?.name ?? "Unknown channel"} | DiscordChatExporter frontend</title>
    <meta name="description" content="Svelte demo app"/>
</svelte:head>

{#if data.messages}
<WatchHash messages={data.messages} />
<section>
    <div class="chatlog" id="main-chatlog" bind:this={mainChatlog}>
        <div class=chatlog__message-group>
            <div id="top" />
            {#key data.channelId}
                {#if data.mainChannelMessage}
                <div class="back-main-channel">
                    <a href="/channels/{data.guildId}/{data.mainChannelMessage.channelId}/#{data.mainChannelMessage.id}">← BACK TO MAIN CHANNEL</a>
                </div>
                {/if}
            {/key}
            {#if mainChatlog}
                <Messages messages={Object.values(data.messages)} guild={data.guild} guildId={data.guildId} channelId={data.channelId} rootId={mainChatlog}/>
            {/if}
            <div id="bottom" />
        </div>
    </div>
</section>
{:else}
<div class="error">
    <p>Channel ID {BigInt(data.channelId)} was not exported</p>
</div>
{/if}

<style>
    .error {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        text-align: center;
        padding: 2rem;
        background-color: var(--panel-messages-bg);
    }
 section {
     background-color: var(--panel-messages-bg);
     /*height: 100vh;*/
 }

 .chatlog {
     overflow-y: auto;
     max-height: calc(100vh - 88px);
     margin-right: 5px;
 }

 .back-main-channel {
     padding: 10px 25px;
     margin-bottom: 5px;
 }
</style>



