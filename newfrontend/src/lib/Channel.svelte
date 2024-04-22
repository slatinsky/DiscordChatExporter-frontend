<script lang="ts">
    import { selectedChannelId } from "../js/stores/guildStore";
    import { threadshown } from "../js/stores/layoutStore";
</script>


<div class="channel" class:threadshown={$threadshown}>
    {$selectedChannelId}
</div>

<style>
    .channel {
        background-color: #313338;
        height: 100%;
    }

    .threadshown {
        border-bottom-right-radius: 8px;
    }
</style>