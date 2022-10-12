<script>
    import './styles.css';

    export let data
    // console.log("data", data);
</script>


<div class="app">
    <div class="guilds">
        <a href="/">HOME</a>
<!--        guild list-->
        {#if data.guilds}
            {#each Object.values(data.guilds) as guild}
                <a href="/channels/{guild.id}">
                    <div><img src="{guild.iconUrl}" alt="{guild.name}"></div>
                </a>

            {/each}
        {/if}
    </div>
    <div class="right">
<!--        others-->
        <main>
            <slot/>
        </main>
    </div>
</div>

<style>
    .app {
        display: grid;
        grid-template-columns: 60px 1fr;
        height: 100vh;
    }
    .guilds {
        background-color: #202225;
        height: 100%;
        overflow-y: auto;
    }

    .right {
        height: 100%;
    }


    img {
        width: 48px;
        height: 48px;
        margin: 5px;
    }
</style>
