<template>
  <div class="breadcrumb">
    <p v-for="breadcrumb in breadcrumbs" :key="breadcrumb.id">
      <nuxt-link
        :to="localePath(breadcrumb.localePath)"
        :disabled="!breadcrumb.name"
      >
        <fa v-if="breadcrumb.id === 'organisation'" icon="home" />
        <template v-else>
          <fa icon="angle-right" size="sm" />
          {{ idToName(breadcrumb.localePath.name) }}
          {{ breadcrumb.text }}
        </template>
      </nuxt-link>
    </p>
  </div>
</template>

<script>
import split from 'lodash/split'
import join from 'lodash/join'

import { mapState, mapGetters } from 'vuex'

export default {
  data() {
    return {
      organisation: this.$gettext('Organisation'),
      'organisation-login': this.$gettext('Login'),
      'organisation-signup': this.$gettext('Signup'),
      'organisation-reset-key': this.$gettext('Reset'),
      // main sections
      'organisation-inventory': this.$gettext('Inventory'),
      'organisation-innovation': this.$gettext('Innovation Portfolio'),
      'organisation-management': this.$gettext('Portfolio Manager'),
      'organisation-initiatives': this.$gettext('My initiatives'),
      // sub sections for inventory
      'organisation-inventory-list': this.$gettext('Inventory'),
      // sub sections for innovation
      // sub sections for managers
      'organisation-management-new': this.$gettext('New portfolio'),
      'organisation-management-id-edit': this.$gettext('Edit portfolio'),
      // sub sections for initiatives
      'organisation-initiatives-create': this.$gettext('New Initiative'),
      'organisation-initiatives-id-published': this.$gettext(
        'Published Initiative'
      ),
      'organisation-initiatives-id-edit': this.$gettext('Edit Initiative'),
      // route exclutions
      exclude: [
        'organisation-inventory-list',
        'organisation-inventory',
        'organisation-edit-profile',
        'organisation-admin',
        'organisation-admin-country',
        'organisation-admin-donor',
        'organisation-admin-import',
        'organisation-admin-import-id',
        'organisation-email-confirmation',
        'organisation-cms',
      ],
    }
  },
  computed: {
    ...mapState({
      portfolioManagementName: (state) => state.portfolio.name,
    }),
    ...mapGetters({
      initiative: 'project/getProjectData',
      portfolioInnovationName: 'portfolio/getName',
    }),
    pureRoute() {
      if (this.$route && this.$route.name) {
        return this.$route.name.split('___')[0]
      }
      return null
    },
    breadcrumbs() {
      let name = ''
      const route = this.exclude.includes(this.pureRoute)
        ? 'organisation'
        : this.pureRoute
      return split(route, '-').map((item, idx) => {
        name = name !== '' ? join([name, item], '-') : item
        return {
          id: item,
          localePath: { name },
          text: this[name] || '',
        }
      })
    },
  },
  methods: {
    idToName(route) {
      switch (route) {
        case 'organisation-initiatives-id':
          return this.initiative.name
        case 'organisation-innovation-id':
          return this.portfolioInnovationName
        case 'organisation-management-id':
          return this.portfolioManagementName
        default:
          return ''
      }
    },
  },
}
</script>

<style lang="less" scoped>
@import '~assets/style/variables.less';

.breadcrumb {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  height: inherit;
  color: @colorWhite;
  p {
    margin: 0 0 0 8px;
    a {
      text-decoration: none;
      transition: @transitionFade;
      font-size: @fontSizeBase;
      letter-spacing: 0;
      line-height: 18px;
      svg {
        margin-right: 8px;
      }
    }
  }
}
</style>
