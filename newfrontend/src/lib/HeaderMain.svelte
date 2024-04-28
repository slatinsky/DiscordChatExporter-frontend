<script lang="ts">
    import { selectedChannel } from "../js/stores/guildStore";
    import { threadshown } from "../js/stores/layoutStore";
    import IconChannel from "./icons/IconChannel.svelte";


</script>


<div class="header-main" class:threadshown={$threadshown}>
    <div class="channel-icon">
        <IconChannel />
    </div>
    <div class="channel-name">{$selectedChannel?.name ?? "Select a channel"}</div>
</div>



<style>
    .channel-icon {
        display: grid;
        place-items: center;
    }
    .header-main {
        height: 100%;
        display: flex;
        flex-direction: row;
        align-items: center;
        padding: 0 15px;
        box-sizing: border-box;
        gap: 5px;
        border-bottom: 1px solid #20222599;
        background-color: #313338;
    }

    .header-main.threadshown {
        border-top-right-radius: 8px;
    }

    .channel-name {
        font-size: 16px;
        font-weight: 600;
        color: #F2F3F5;
        flex-grow: 3;
    }
</style>