<script lang="ts">
    import { isDateDifferent } from '../../js/helpers';
    import { fetchSearch, fetchSearchCount } from '../../js/stores/api';
    import { findChannel, findThread, getGuildState, isChannel } from '../../js/stores/guildState.svelte';
    import { getLayoutState } from '../../js/stores/layoutState.svelte';
    import DateSeparator from '../DateSeparator.svelte';
    import InfiniteScroll3 from '../InfiniteScroll3.svelte';
    import Icon from '../icons/Icon.svelte';
    import ChannelIcon from '../menuchannels/ChannelIcon.svelte';
    import Message from '../message/Message.svelte';
    import { getSearchState } from './searchState.svelte';

    const guildState = getGuildState()
    const searchState = getSearchState();
    const layoutState = getLayoutState()
    let apiGuildId = $derived(guildState.guildId ? guildState.guildId : "000000000000000000000000")



    function addCommas(count: number) {
        return count.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    async function fetchMessagesWrapper(direction: "before" | "after" | "around" | "first" | "last", messageId: string | null = null, limit: number) {
        return fetchSearch(apiGuildId, searchState.searchPrompt, direction, messageId, limit)
    }
</script>

{#snippet renderMessageSnippet2(message, previousMessage)}
    <div data-messageid={message._id}>
        {#if !previousMessage || previousMessage.channelId !== message.channelId}
            {@const channelObj = findChannel(message.channelId)}
            {@const threadObj = findThread(message.channelId)}
            {#if threadObj}
                {@const parentChannelObj = findChannel(threadObj.categoryId)}
                <div class="channelthread-name-wrapper">
                    <button class="thread-name" onclick={()=>guildState.changeThreadId(threadObj._id, null)}>
                        <ChannelIcon channel={threadObj} width={16} />{threadObj.name}
                    </button>
                    <button class="channel-name-small" onclick={()=>guildState.changeChannelId(parentChannelObj._id, null)}>
                        <ChannelIcon channel={parentChannelObj} width={12} />{parentChannelObj?.name}
                    </button>
                </div>
            {:else if channelObj}
                <div class="channelthread-name-wrapper">
                    <button class="channelthread-name"  onclick={()=>{
                        if (isChannel(channelObj._id)) {
                            guildState.changeChannelId(channelObj._id, null)
                        } else {
                            guildState.changeThreadId(channelObj._id, null)
                        }
                    }}>
                        <ChannelIcon channel={channelObj} width={16} />{channelObj.name}
                    </button>
                </div>
            {/if}
        {/if}
        {#if isDateDifferent(previousMessage, message)}
            <DateSeparator messageId={message._id} />
        {/if}
        <div class="searchresult-message-wrapper">
            <Message message={message} previousMessage={previousMessage} showJump={true} mergeMessages={false} />
        </div>
    </div>
{/snippet}

{#snippet emptySnippet()}
    <div class="channel-wrapper">
        <div class="no-results-wrapper">
            <div class="no-results-inner">
                <Icon name="placeholder/no-search-results" width={160} height={160} />
                <div class="no-results-msg">We searched far and wide. Unfortunately, no results were found.</div>
            </div>
        </div>
    </div>
{/snippet}


<div class="channel-wrapper">
    {#key searchState.submittedSearchPrompt}
        {#if searchState.submittedSearchPrompt !== ""}
            <div class="search-header">
                <div class="header-txt">
                    {#await fetchSearchCount(apiGuildId, searchState.submittedSearchPrompt)}
                        Searching... <div class="spinner"></div>
                    {:then count}
                        {#if count === 0}
                            No Results
                        {:else}
                            {addCommas(count)} Results
                        {/if}
                    {:catch error}
                        <p style="color: red">{error.message}</p>
                    {/await}
                </div>
            </div>
            <div class="scrollwrapper" class:ismobile={layoutState.mobile}>
                <InfiniteScroll3
                    fetchMessages={fetchMessagesWrapper}
                    guildId={apiGuildId}
                    scrollToMessageId={"last"}
                    snippetMessage={renderMessageSnippet2}
                    emptySnippet={emptySnippet}
                />
            </div>
        {/if}
    {/key}
</div>


<style>
    .spinner {
        border: 2px solid rgba(0, 0, 0, 0);
        border-left-color: #D6D9DC;
        border-radius: 50%;
        width: 16px;
        height: 16px;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }


    .channelthread-name-wrapper {
        display: flex;
        gap: 8px;

        margin: 18px 4px 8px 14px;
        .channelthread-name {
            display: flex;
            gap: 4px;
            font-size: 16px;

            align-items: center;

            cursor: pointer;
        }
        .channelthread-name:hover {
            text-decoration: underline;
        }
        .channel-name-small {
            display: flex;
            gap: 4px;
            font-size: 12px;
            color: #b5bac1;
            align-items: center;
            cursor: pointer;
        }
        .channel-name-small:hover {
            text-decoration: underline;
        }
        .thread-name {
            display: flex;
            gap: 4px;
            font-size: 16px;
            align-items: center;
            cursor: pointer;
        }
        .thread-name:hover {
            text-decoration: underline;
        }
    }
    .searchresult-message-wrapper {
        border-radius: 8px;
        margin: 6px 16px 8px 16px;
        padding: 1px 0 11px 0;
        background-color: #313338;
    }

    .no-results-wrapper {
        display: grid;
        place-items: center;
        background-color: #2b2d31;
        color: #b5bac1;
        font-size: 16px;
        padding: 16px;
        height: 100%;
        .no-results-inner {
            display: flex;
            flex-direction: column;
            gap: 40px;
            align-items: center;

            .no-results-msg {
                max-width: 280px;
                color: #dbdee1;
                font-size: 16px;
                font-weight: 500;
                text-align: center;
            }
        }


    }

    .channel-wrapper {
        height: 100%;

        display: flex;
        flex-direction: column;
        overflow: hidden;


        .search-header {
            width: 100%;
            height: 56px;
            background-color: #1e1f22;
            font-size: 16px;


            display: flex;
            align-items: center;

            .header-txt {
                font-size: 16px;
                font-weight: 400;
                color: #f2f3f5;
                padding: 0 16px;
                height: 50px;
                display: flex;
                align-items: center;
                gap: 12px;
            }
        }

        .scrollwrapper {
            height: calc(100% - 56px);
        }
        .scrollwrapper.ismobile {
            height: calc(100% - 56px - 47px);
        }
    }
</style>