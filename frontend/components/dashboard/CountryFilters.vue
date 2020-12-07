<template>
  <div class="CountryFilters">
    <region-select v-model="selectedRegion" />
    <country-office-select
      v-model="selectedCountryOffice"
      :region-filter="selectedRegion"
      :multiple="true"
    />
    <country-select
      v-model="selectedCountries"
      :region="selectedRegion"
      :disabled="disabledCountries"
    />
    <regional-select
      v-model="selectedRegionalOffice"
      :disabled="disabledCountries"
    />
  </div>
</template>

<script>
import CountryOfficeSelect from '@/components/common/CountryOfficeSelect'
import { mapGetters, mapState, mapActions } from 'vuex'
import { mapGettersActions } from '../../utilities/form.js'

import CountrySelect from '../common/CountrySelect'
import RegionSelect from '../common/RegionSelect'
import RegionalSelect from '~/components/common/RegionalSelect'

export default {
  components: {
    CountrySelect,
    CountryOfficeSelect,
    RegionSelect,
    RegionalSelect,
  },
  computed: {
    ...mapGetters({
      dashboardType: 'dashboard/getDashboardType',
      regionalOffices: 'projects/getRegionalOffices',
    }),
    ...mapState({
      office: (state) => state.offices.office,
      offices: (state) => state.offices.offices,
    }),
    ...mapGettersActions({
      selectedRegionalOffice: [
        'dashboard',
        'getFilteredRegionalOffice',
        'setFilteredRegionalOffice',
      ],
      selectedCountries: [
        'dashboard',
        'getFilteredCountries',
        'setFilteredCountries',
      ],
      selectedRegion: ['dashboard', 'getFilteredRegion', 'setFilteredRegion'],
      selectedCountryOffice: [
        'dashboard',
        'getFilteredCountryOffice',
        'setFilteredCountryOffice',
      ],
    }),
    disabledCountries() {
      return !!(
        this.selectedCountryOffice && this.selectedCountryOffice.length > 0
      )
    },
  },
  watch: {
    selectedCountries(newCountries, oldCountries) {
      if (
        !newCountries ||
        !newCountries.length ||
        (oldCountries &&
          oldCountries.length &&
          oldCountries[0] !== newCountries[0])
      ) {
        this.selectedOffice = null
      }
    },
    selectedRegion(newRegion) {
      this.selectedCountries = Number.isInteger(newRegion)
        ? this.selectedCountries.filter((c) => c.unicef_region === newRegion.id)
        : this.selectedCountries
    },
    async selectedCountryOffice(newOffices) {
      this.selectedCountries = Array.isArray(newOffices)
        ? this.offices
            .filter((o) => newOffices.includes(o.id))
            .map((c) => c.country)
        : this.offices.filter((o) => newOffices === o.id).map((c) => c.country)

      await this.$store.dispatch(
        'offices/loadOffice',
        newOffices ? newOffices[0] : 0
      )
      this.selectedRegionalOffice =
        this.office && newOffices && newOffices.length === 1
          ? [this.office.regional_office]
          : null
    },
  },
  mounted() {
    this.loadOffices()
  },
  methods: {
    ...mapActions({
      loadOffices: 'offices/loadOffices',
    }),
  },
}
</script>

<style lang="less">
@import '~assets/style/variables.less';
@import '~assets/style/mixins.less';

.CountryFilters {
  .el-select {
    width: 100%;
    margin-bottom: 10px;

    &:last-child {
      margin-bottom: 0;
    }
  }
}
</style>
