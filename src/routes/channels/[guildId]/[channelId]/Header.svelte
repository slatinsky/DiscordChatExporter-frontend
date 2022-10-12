<script>
	import Search from "./Search.svelte";


    export let channel;
    export let messages
    
</script>

<section>
    <div class="channel-header">
        <div class="channel-header__left">
            <div class="channel-name"># {channel.name}</div>
            <div class="topic">| {channel.topic}</div>
            <Search messages={messages}></Search>
            
        </div>
    </div>
</section>


<style>
    .channel-header__left {
        display: flex;
        flex-direction: row;
        align-items: center;

        gap: 15px;

        padding: 10px 20px;
    }

    .channel-name {
        font-size: 1.5rem;
        font-weight: 700;
    }

    .topic {
        font-size: 1rem;
        font-weight: 400;
        color: gray;
    }


</style>