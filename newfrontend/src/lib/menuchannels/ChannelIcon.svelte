<script lang="ts">
    import type { Channel } from "../../js/interfaces";
    import Icon from "../icons/Icon.svelte";

	interface MyProps {
        channel: Channel;
        width: number;
    }
    let { channel, width }: MyProps = $props();
</script>
{#if channel.threads && channel.threads.length > 0}
    <Icon name="channeltype/channelWithThreads" width={width} />
{:else if channel.type == "GuildVoiceChat"}
    <Icon name="channeltype/voice" width={width} />
{:else if channel.type == "GuildNews"}
    <Icon name="channeltype/news" width={width} />
{:else if channel.type == "GuildPublicThread" || channel.type == "GuildPrivateThread"}
    <Icon name="channeltype/thread" width={width} />
{:else}
    <Icon name="channeltype/channel" width={width} />
{/if}