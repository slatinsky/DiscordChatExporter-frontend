<script lang="ts">
    export let title: string;
    export let description: string | undefined = undefined;
</script>

<p class="title">{title}</p>
{#if description}
    <p class="description">{description}</p>
{/if}
<div class="radios">
    <slot />
</div>

<style>
    .title {
        color:#a9bac1;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .02em;
        font-size: 12px;
        line-height: 16px;
    }
    .description {
        color: #b5bac1;
        font-size: 14px;
        line-height: 20px;
        font-weight: 400;
    }
    .radios {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}
</style>