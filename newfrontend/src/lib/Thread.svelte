<script lang="ts">
    import { selectedThread, selectedThreadId } from "../js/stores/guildStore";


</script>


<div class="thread-wrapper">
    <div class="header-main">
        <div class="thread-name">{$selectedThread?.name ?? "Select a thread"}</div>
    </div>
    <div class="thread">
        {$selectedThreadId}
    </div>
</div>


<style>
    .thread-wrapper {
        height: 100%;
        margin-left: 7px;
        background-color: #313338;

        border-top-left-radius: 8px;
        border-bottom-left-radius: 8px;
    }
    .header-main {
        height: 47px;
        display: flex;
        flex-direction: row;
        align-items: center;
        padding: 5px 10px 5px 15px;
        box-sizing: border-box;
        gap: 5px;
        border-bottom: 1px solid #20222599;
    }

    .thread-name {
        font-size: 16px;
        font-weight: 600;
        color: #F2F3F5;
        flex-grow: 3;
    }
</style>