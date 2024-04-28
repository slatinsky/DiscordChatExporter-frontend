<script lang="ts">
    export let value: any;
    export let group: any;
    export let name: string;

    export let title: string;

    $: isSelected = value === group;
</script>

<label class:selected={isSelected}>
    {#if isSelected}
        <svg aria-hidden="true" role="img" width="24" height="24" viewBox="0 0 24 24"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12 4C7.58172 4 4 7.58172 4 12C4 16.4183 7.58172 20 12 20ZM12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" fill="currentColor"></path><circle cx="12" cy="12" r="5" class="radioIconForeground-3wH3aU" fill="currentColor"></circle></svg>
    {:else}
        <svg aria-hidden="true" role="img" width="24" height="24" viewBox="0 0 24 24"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12 4C7.58172 4 4 7.58172 4 12C4 16.4183 7.58172 20 12 20ZM12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" fill="currentColor"></path></svg>
    {/if}
    <span class="circle"></span>
    <input type="radio" {name} {value} bind:group hidden/>
    <div>
        <div class="title">{title}</div>
    </div>
</label>

<style>
    label {
        background-color: #2b2d31;
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 5px;
        padding: 10px;
        cursor: pointer;
    }

    label.selected {
        background-color: #43444b;
    }

    input {
        margin-right: 10px;
    }

    .title {
        font-weight: 500;
        font-size: 16px;
    }

    .selected .title {
        color: #fff;
    }
</style>