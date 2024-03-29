<template>
  <div class="LandingPage">
    <WelcomeSection />
    <InitiativesSection />
    <NewsSection />
    <div class="MapBoxContainer">
      <LandingMap v-if="!showCoverImage" />
      <CountryProjectsBox />
      <div v-if="showCoverImage" :style="{ backgroundImage: `url(${landingData.cover_url})` }" class="CoverImageBg" />
    </div>
    <AboutSection />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import LandingMap from '@/components/landing/LandingMap.vue'
import WelcomeSection from '@/components/landing/WelcomeSection.vue'
import CountryProjectsBox from '@/components/landing/CountryProjectsBox.vue'
import InitiativesSection from '@/components/landing/InitiativesSection.vue'
import NewsSection from '@/components/landing/NewsSection.vue'
import AboutSection from '@/components/landing/AboutSection.vue'

export default {
  components: {
    LandingMap,
    WelcomeSection,
    CountryProjectsBox,
    InitiativesSection,
    NewsSection,
    AboutSection,
  },
  async fetch({ store }) {
    await store.dispatch('landing/resetSearch')
    await store.dispatch('dashboard/setDashboardSection', 'map')
    await Promise.all([
      store.dispatch('projects/loadProjectStructure'),
      store.dispatch('countries/loadMapData'),
      store.dispatch('offices/loadOffices'),
      store.dispatch('projects/loadLandingProjects'),
      store.dispatch('landing/loadNewsFeed'),
    ])
    await store.dispatch('dashboard/loadProjectsMap')
  },
  computed: {
    ...mapGetters({
      landingData: 'landing/getLandingPageData',
      landingProjects: 'projects/getLandingProjects',
    }),
    showCoverImage() {
      return this.landingData && this.landingData.cover
    },
  },
}
</script>

<style lang="less">
@import '~assets/style/variables.less';
@import '~assets/style/mixins.less';

.LandingPage {
  .MapBoxContainer {
    position: relative;
  }

  .CoverImageBg {
    display: block;
    height: @landingMapHeight;
    min-height: @landingMapMinHeight;
    background-color: @colorGrayLight;
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
  }

  .CoverImage {
    width: 100%;
    height: auto;
  }

  h2 {
    font-size: @fontSizeHeading;
  }

  h3 {
    font-size: @fontSizeTitle;
  }

  h4 {
    font-size: @fontSizeLarge;
  }

  h6 {
    font-size: @fontSizeMedium;
    line-height: 24px;
    font-weight: 400;
  }
}
</style>
