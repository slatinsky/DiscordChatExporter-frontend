<script lang="ts">
    // this file handles app layout
    import {throttle} from 'lodash-es';

    import MenuCategories from "./lib/menuchannels/MenuCategories.svelte";
    import Guilds from "./lib/Guilds.svelte";
    import HeaderMain from "./lib/HeaderMain.svelte";
    import SearchResults from "./lib/search/SearchResults.svelte";
    import Channel from "./lib/Channel.svelte";
    import Thread from "./lib/Thread.svelte";
    import Settings from "./lib/settings/Settings.svelte";
    import ContextMenu from "./lib/components/menu/ContextMenu.svelte";
    import { onMount } from "svelte";
    import { position } from "./js/stores/menuStore";
    import { font, hideSpoilers, theme } from './js/stores/settingsStore.svelte';
    import { getGuildState, isChannel } from './js/stores/guildState.svelte';
    import { getLayoutState } from './js/stores/layoutState.svelte';
    import ViewUser from './lib/viewuser/ViewUser.svelte';
    import ImageGallery from './lib/imagegallery/ImageGallery.svelte';

    onMount(() => {
      const unsubscribe1 = theme.subscribe(value => {
        document.documentElement.setAttribute('data-theme', value);
      });

      const unsubscribe2 = hideSpoilers.subscribe(value => {
        document.documentElement.setAttribute('data-hidespoilers', value);
      });

      const unsubscribe3 = font.subscribe(value => {
        document.documentElement.setAttribute('data-font', value);
      });

      return () => {
        unsubscribe1()
        unsubscribe2()
        unsubscribe3()
      }
    })

    const guildState = getGuildState()
    const layoutState = getLayoutState()

    /* capture mouse position for right click context menu */
    function handleMousemove(event) {
      $position = { x: event.clientX, y: event.clientY };
    }
    const handleThrottledMousemove = throttle(handleMousemove, 100, { leading: false, trailing: true });


    // called from parsed markdown channel and message links
    // window.globalSetGuild = async (guildId: string) => {
    //   await guildState.changeGuildId(guildId)
    //   await guildState.pushState()
    // }
    window.globalSetChannel = async (guildId: string, channelId: string) => {
      await guildState.comboSetGuildChannel(guildId, channelId)
      await guildState.pushState()
    }
    window.globalSetMessage = async (guildId: string, channelId: string, messageId: string) => {
      await guildState.comboSetGuildChannelMessage(guildId, channelId, messageId)
      await guildState.pushState()
    }
</script>

<svelte:head>
    <title>DCE-Frontend</title>
    <meta name="description" content="View your JSON DiscordChatExporter exports as if you were using Discord interface"/>
</svelte:head>

<ViewUser />
<ImageGallery />

<div style="width: 100%;height: 100%;">
  <main
    class:mobile={layoutState.mobile} class:desktop={!layoutState.mobile}
    class:searchshown={layoutState.searchshown} class:searchhidden={!layoutState.searchshown}
    class:mobilesidepanelshown={layoutState.mobilesidepanelshown} class:mobilesidepanelhidden={!layoutState.mobilesidepanelshown}
    class:threadshown={layoutState.threadshown} class:threadhidden={!layoutState.threadshown}
    on:mousemove={handleThrottledMousemove}
    >
      <div class="guilds"><Guilds /></div>
      <div class="channels"><MenuCategories /></div>
      <div class="header-main"><HeaderMain /></div>
      <div class="channel"><Channel /></div>
      <div class="search-results"><SearchResults /></div>
      <div class="thread"><Thread /></div>
    </main>
  <div class="settings" class:settingsshown={layoutState.settingsshown}><Settings /></div>
  <ContextMenu />
</div>

<style>
  .settings {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: none;
    z-index: 200;
    background-color: #2B2D31;
  }
  .settings.settingsshown {
    display: block;
  }


  .guilds {
    grid-area: guilds;
  }
  .channels {
    grid-area: channels;
  }
  .header-main {
    grid-area: header-main;
  }
  .channel {
    grid-area: channel;
    overflow: hidden;
  }
  .search-results {
    grid-area: search-results;
    background-color: #2B2D31;
    overflow: hidden;
  }
  .thread {
    grid-area: thread;


  }

  /*Grid items have an initial size of min-width: auto and min-height: auto, prevent overflow*/
  .guilds,
  .channels,
  .header-main,
  .channel,
  .thread {
    min-width: 0;
    min-height: 0;
  }

  /* COMMON */
  main {
    display: grid;
    width: 100%;
    height: calc(100% - 7px);
    background-color: #1E1F22;
    margin: 7px 0 0 0;
    box-sizing: border-box;
  }
  main.mobile {
    margin: 0;
  }

  /* DESKTOP NO SEARCH, NO THREAD */
  main.desktop.searchhidden.threadhidden {
    grid-template-areas:
    "guilds channels header-main"
    "guilds channels        channel";
    grid-template-columns: 70px 236px 1fr;
    grid-template-rows: 47px 1fr;
  }
  main.desktop.searchhidden.threadhidden .search-results {
    display: none;
  }
  main.desktop.searchhidden.threadhidden .thread {
    display: none;
  }



  /* DESKTOP NO SEARCH, THREAD SHOWN */
  main.desktop.searchhidden.threadshown {
    grid-template-areas:
    "guilds channels header-main    thread"
    "guilds channels        channel thread";
    grid-template-columns: 70px 236px 1fr 1fr;
    grid-template-rows: 47px 1fr;
  }
  main.desktop.searchhidden.threadshown .search-results {
    display: none;
  }


  /* DESKTOP WITH SEARCH */
  main.desktop.searchshown.threadhidden,
  main.desktop.searchshown.threadshown {
    grid-template-areas:
    "guilds channels header-main    header-main   "
    "guilds channels        channel search-results";

    grid-template-columns: 70px 236px 1fr 420px;
    grid-template-rows: 47px 1fr;
  }
  main.desktop.searchshown.threadshown .search-results,
  main.desktop.searchshown.threadhidden .search-results {
    display: block;
  }
  main.desktop.searchshown.threadshown .thread,
  main.desktop.searchshown.threadhidden .thread {
    display: none;
  }





  /* MOBILE */

  /* hide hidden elements */
  main.mobile.threadhidden .thread,
  main.mobile.searchhidden .search-results {
    display: none;
  }


  /* animate side panel */
  main.mobile .header-main,
  main.mobile .channel,
  main.mobile .thread {
    transition: left 0.2s;
  }


  /* main mobile layout, other elements are positioned absolutely */
  main.mobile {
    width: calc(100vw + 70px + min(236px, 100svw - 100px));
    grid-template-areas:
    "guilds channels";
    grid-template-columns: 70px min(236px, 100svw - 100px);
    grid-template-rows: 1fr;
  }

  /* absolute positioning for mobile elements */
  main.mobile .header-main {
    position: absolute;
    width: 100%;
    height: 47px;
    top: 0;
    left: 0;
  }
  main.mobile .channel {
    position: absolute;
    width: 100%;
    height: calc(100% - 47px);
    top: 47px;
    left: 0;
  }
  main.mobile .thread {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
  }
  main.mobile .search-results {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 47px;
    left: 0;
  }

  /* side panel shown */
  main.mobile.mobilesidepanelshown .channel,
  main.mobile.mobilesidepanelshown .header-main,
  main.mobile.mobilesidepanelshown .thread {
    left: calc(70px + min(236px, 100svw - 100px));
  }

  main.mobile.searchshown .header-main {
    left: 0;
  }
</style>