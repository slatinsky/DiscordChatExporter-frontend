<script>
    export let content
    let processedContent
    function process(content) {
        processedContent = window.discordMarkdown.toHTML(content);
    }

    $: process(content)
</script>

<div>{@html processedContent}</div>
