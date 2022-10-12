<script>
    // import Preamble from "../../../components/Preamble.svelte";
	import Header from "./Header.svelte";
	import Messages from "./Messages.svelte";

    let title = "JSON READER";

    export let data;
    // console.log('data3', data);




</script>

<svelte:head>
    <title>{title}</title>
    <meta name="description" content="Svelte demo app"/>
</svelte:head>

<section>
    <!-- {#if messages} -->
        <Header channel={data.channel} messages={data.messages} />
        <!-- {#each data.messages as message} -->
            <!-- <Message message={message}/> -->
        <!-- {/each} -->
        <div class="chatlog">
            <div class=chatlog__message-group>
                <Messages messages={data.messages} authors={data.guild.authors} emojis={data.guild.emojis}/>
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
 }
</style>



