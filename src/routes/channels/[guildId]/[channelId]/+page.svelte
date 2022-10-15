<script>
	import { onMount } from "svelte";

    // import Preamble from "../../../components/Preamble.svelte";
import Header from "./Header.svelte";
	import Messages from "./Messages.svelte";

    let title = "DiscordChatExporter frontend";

    export let data;
    // console.log('data3', data);


    onMount(() => {

	});

</script>

<svelte:head>
    <title>{title}</title>
    <meta name="description" content="Svelte demo app"/>
</svelte:head>

<section>
    <!-- {#if messages} -->
    {#key data.channelId}
    <Header channel={data.channel} messages={data.messages} />
    {/key}
        <!-- {#each data.messages as message} -->
            <!-- <Message message={message}/> -->
        <!-- {/each} -->
    <div class="chatlog">
        <div class=chatlog__message-group>
            <div id="top" />
            {#key data.channelId}
                {#if data.mainChannelMessage}
                <div class="back-main-channel">
                    <a href="/channels/{data.guildId}/{data.mainChannelMessage.channelId}/#{data.mainChannelMessage.id}">← BACK TO MAIN CHANNEL</a>
                </div>
                {/if}
            {/key}
            <Messages messages={data.messages} authors={data.guild.authors} emojis={data.guild.emojis} guildId={data.guildId} channelId={data.channelId}/>

            <div id="bottom" />
        </div>
    </div>

<!--        <Postamble messageCount="{messages.length}"/>-->
<!--        <pre>{JSON.stringify(json, null, 2)}</pre>-->
    <!-- {:else}
        {#if isError}
            <p>ERROR</p>
        {:else}
            <p>Loading...</p>
        {/if} -->

    <!-- {/if} -->
</section>

<style>
 section {
     background-color: #36393F;
     /*height: 100vh;*/
 }

 .chatlog {
     overflow-y: auto;
     max-height: calc(100vh - 96px);
     margin-right: 5px;
 }

 .back-main-channel {
     padding: 10px 25px;
     margin-bottom: 5px;
 }
</style>



