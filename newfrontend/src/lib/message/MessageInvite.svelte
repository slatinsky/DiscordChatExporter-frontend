<script lang="ts">
    import { getLayoutState } from "../../js/stores/layoutState.svelte";
    import Icon from "../icons/Icon.svelte";

	interface MyProps {
        inviteId: string;
    }
    let { inviteId }: MyProps = $props();
    let inviteLink = `https://discord.gg/${inviteId}`;

    const layoutState = getLayoutState()
</script>


<div class="invite">
    <div class="invite-title">You've been invited to join a server</div>
    <div class="invite-content-row">
        <div class="invite-guild-icon">
            <Icon name="dcef/filled" width={30} />
        </div>
        <div class="text-col">
            <a class="guild-name" target="_blank" href={inviteLink}>Unknown Server</a>
            <div class="invite-status-wrapper">
                <div class="green-circle"></div>
                <div class="status-text" style="margin-right: 7px;">N/A Online</div>
                <div class="gray-circle"></div>
                <div class="status-text">N/A Members</div>
            </div>
        </div>
        {#if !layoutState.mobile}
            <div class="spacer"></div>
            <a class="join-btn" target="_blank" href={inviteLink}>Join</a>
        {/if}
    </div>
    {#if layoutState.mobile}
        <a class="join-btn join-btn-mobile" target="_blank" href={inviteLink}>Join</a>
    {/if}

</div>

<style>
    .invite {
        background-color: #2B2D31;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        max-width: 400px;
        width: 100%;
        box-sizing: content-box;
    }
    .invite-title {
        font-weight: 700;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
        text-transform: uppercase;
        font-size: 12px;
        color: #A9BAC1;
    }
    .invite-content-row {
        display: flex;
        gap: 16px;
        align-items: center;
    }
    .invite-guild-icon {
        width: 50px;
        height: 50px;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: #5D6BEE;
        border-radius: 25%;
        padding: 5px;
    }
    .text-col {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    .guild-name {
        font-size: 16px;
        color: white;
        font-weight: 600;
        text-decoration: none;
    }
    .guild-name:hover {
        text-decoration: underline;
    }

    .invite-status-wrapper {
        display: flex;
        gap: 5px;
        align-items: center;
    }

    .green-circle {
        width: 8px;
        height: 8px;
        background-color: #56A15D;
        border-radius: 50%;
    }
    .gray-circle {
        width: 8px;
        height: 8px;
        background-color: #81848D;
        border-radius: 50%;
    }

    .status-text {
        font-size: 14px;
        color: #b6bac1;
    }

    .spacer {
        flex: 1;
    }

    .join-btn {
        background-color: #457D49;
        color: white;
        border-radius: 3px;
        width: 73px;
        height: 40px;
        font-size: 14px;
        cursor: pointer;
        font-weight: 500;
        text-decoration: none;

        display: grid;
        place-items: center;
    }
    .join-btn:hover {
        background-color: #346036;
    }
    .join-btn-mobile {
        width: 100%;
    }

</style>