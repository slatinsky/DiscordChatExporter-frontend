<script lang="ts">
    import { selectedChannelMessageIds, selectedGuildId } from "../js/stores/guildStore";
    import { threadshown } from "../js/stores/layoutStore";
    import InfiniteScroll from "./InfiniteScroll.svelte";
    import Message from "./message/Message.svelte";
</script>


<div class="channel-wrapper" class:threadshown={$threadshown}>
    <div class="channel" >
        <InfiniteScroll ids={$selectedChannelMessageIds} guildId={$selectedGuildId}>
            <div slot="item" let:message>
                <Message message={message} />
            </div>
        </InfiniteScroll>
    </div>
</div>


<style>
    .channel-wrapper {
        height: 100%;
        overflow: hidden;
    }

    .threadshown {
        border-bottom-right-radius: 8px;
    }
    .channel {
        background-color: #313338;
        height: 100%;
    }
</style>