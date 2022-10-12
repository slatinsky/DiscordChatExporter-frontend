<script>
    export let id = null;
    export let name = null;
    export let iconUrl = null;
    export let channelCategory = null;
    export let channelName = null;
</script>

<!--<div class="preamble">-->
<!--    <div class="preamble__guild-icon-container">-->
<!--        <img-->
<!--            class="preamble__guild-icon"-->
<!--            src="{iconUrl}"-->
<!--            alt="Guild icon"-->
<!--            loading="lazy"-->
<!--        />-->
<!--    </div>-->
<!--    <div class="preamble__entries-container">-->
<!--        <div class="preamble__entry">{name}</div>-->
<!--        <div class="preamble__entry">{channelCategory} / {channelName}</div>-->
<!--    </div>-->
<!--</div>-->

<div class="c-preamble">
    <h1># {channelName}</h1>
</div>


<style>
    .c-preamble {
        display: flex;
        align-items: center;
        justify-content: left;
        height: 60px;
        background-color: #2f3136;
        padding-left: 15px;
    }
</style>