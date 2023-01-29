<!-- Container to center the page content -->

<div class="container">
	<slot />
</div>

<style>
    .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        text-align: center;
		padding: 2rem;
    }
</style>