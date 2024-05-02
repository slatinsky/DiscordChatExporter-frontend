<script lang="ts">
    import { getGuildState } from "../js/stores/guildState.svelte";
    import { threadshown } from "../js/stores/layoutStore";
    import InfiniteScroll from "./InfiniteScroll.svelte";
    import Message from "./message/Message.svelte";

    const guildState = getGuildState()
</script>


<div class="channel-wrapper" class:threadshown={$threadshown}>
    <div class="channel" >
        <InfiniteScroll ids={guildState.channelMessagesIds} guildId={guildState.guildId} selectedMessageId={guildState.channelMessageId}>
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