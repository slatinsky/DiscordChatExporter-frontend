<script lang="ts">
    export let photo: string;
    export let name1: string;
    export let name2: string;
</script>

<div class="user-switcher" on:click>
    <img src={photo} alt="" on:error={e => e.target.src = '/favicon.png'} />
    <div>
        <div class="user-switcher-name1">{name1}</div>
        <div class="user-switcher-name2">{name2}</div>
    </div>
</div>


<style>
    .user-switcher {
		height: 31px;
		margin-right: 8px;
		display: flex;
		align-items: center;
		padding: 5px 10px 5px 5px;
		border-radius: 4px;
		cursor: pointer;
        overflow: hidden;
	}

	.user-switcher img {
		margin-right: 8px;
		border-radius: 50%;
        width: 32px;
        height: 32px;
	}
	.user-switcher .user-switcher-name1 {
		font-size: 14px;
		line-height: 18px;
		font-weight: 400;
		color: #F2F3F5;
	}

	.user-switcher .user-switcher-name2 {
		font-size: 12px;
		line-height: 16px;
		font-weight: 400;
		color: #B5BAC1;
	}

    .user-switcher .user-switcher-name1,
    .user-switcher .user-switcher-name2 {
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

	.user-switcher:hover {
		background-color: #3d3e45;
	}
</style>