<script lang="ts">
	import type { Author } from 'src/js/interfaces';
	import ImageGallery from './ImageGallery.svelte';
	export let author: Author

    let showAuthor = false;

    export function viewAuthor() {
        showAuthor = true;
	}
</script>



{#if showAuthor}
    <div class="gallery-wrapper" on:click={()=>showAuthor=false}>
        <div class="gallery-closebtn" on:click={()=>showAuthor=false}>&times;</div>
        <div id="profile" on:click|stopPropagation>
            <ImageGallery asset={author?.avatar} imgclass={"profile-avatar"} />
            <div class="profile-background"></div>

            <div class="profile-inner">
                <div class="profile-header">
                    <div class="profile-nickname">{author.nickname}</div>
                    <div class="profile-name">{author.name}</div>
                </div>
                <div class="profile-scroll">
                    <div class="mini-title">ROLES</div>
                    <div class="roles-wrapper">
                        {#if author.roles}
                            {#each author.roles as role}
                                <div class="role">
                                    <div class="role-color" style={`background-color: ${role.color ?? "#c4c9ce"};`}></div>
                                    <div class="role-name">{role.name}</div>
                                </div>
                            {/each}
                        {:else}
                            <div class="profile-error">Roles not exported</div>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}
<style>
    .gallery-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.8);
        z-index: 1000;
        display: flex;
        justify-content: center;
        align-items: center;

        display: flex;
        flex-direction: column;

        text-align: left;
    }

    .gallery-closebtn {
        position: absolute;
        top: -15px;
        right: 0;
        padding: 10px;
        color: white;
        cursor: pointer;

        font-size: 3rem;
        font-weight: 600;
    }

    #profile {
        width: 100%;
        max-width: 340px;
        height: 548px;
        max-height: 95svh;
        border-radius: 8px;

        background-color: #232428;
        color: #f2f3f5;

        position: relative;
        display: flex;
        flex-direction: column;

    }

    .profile-background {
        width: 100%;
        height: 60px;
        background-color: #383a40;
        position: absolute;
        top: 0;
        left: 0;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }

    :global(.profile-avatar) {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        margin: 1rem 1rem 0 1rem;
        z-index: 1010;
        position: relative;
        border: 7px solid #232428;
        cursor: pointer;
    }

    .profile-inner {
        background-color: #111214;
        margin: 5px 1rem 1rem 1rem;
        border-radius: 8px;
        position: relative;

        display: flex;
        flex-direction: column;
        height: inherit;
        height: calc(100% - 130px);
    }

    .profile-header {
        padding: 12px;
        border-bottom: 1px solid #2f3136;
    }

    .profile-scroll {
        overflow-x: hidden;
        overflow-y: auto;
        padding: 12px;

        height: 100%;

    }

    .profile-nickname {
        font-size: 20px;
        font-weight: 600;
        line-height: 24px;
    }

    .profile-name,
    .profile-error {
        word-break: break-all;
        font-size: 14px;
        line-height: 18px
    }

    .mini-title {
        font-weight: 700;
        margin-bottom: 6px;
        font-size: 12px;
        line-height: 16px;
        text-transform: uppercase;
        letter-spacing: .02em;
    }

    .roles-wrapper {
        display: flex;
        flex-wrap: wrap;
        margin-bottom: 12px;
    }

    .role {
        display: flex;
        gap: 1px;
        align-items: center;

        background-color: #232428;
        border-radius: 4px;

        font-size: 12px;
        font-weight: 500;
        padding: 4px;
        margin: 0 4px 4px 0;

    }

    .role-color {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 6px;
    }
</style>