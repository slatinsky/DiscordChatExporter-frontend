<script>
    export let content
    let processedContent
    function process(content) {
        processedContent = window.discordMarkdown.toHTML(content);
    }

    $: process(content)
</script>

<span>{@html processedContent}</span>
