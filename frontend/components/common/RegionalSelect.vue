<template>
  <lazy-el-select
    v-model="innerValue"
    :multiple="multiple"
    :disabled="disabled"
    :placeholder="$gettext('Multicountry or Regional Office ') | translate"
    filterable
    clearable
    popper-class="CountrySelectorPopper"
    class="CountrySelector"
  >
    <el-option
      v-for="office in regionalOffices"
      :key="office.id"
      :label="office.name"
      :value="office.id"
    />
  </lazy-el-select>
</template>

<script>
import { mapGetters } from 'vuex'
export default {
  model: {
    prop: 'value',
    event: 'change',
  },
  props: {
    value: {
      type: Number,
      default: null,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    offices: {
      type: Array,
      default: () => [],
    },
  },
  computed: {
    ...mapGetters({
      regionalOffices: 'projects/getRegionalOffices',
    }),
    innerValue: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit('change', value)
      },
    },
    multiple() {
      return Array.isArray(this.value)
    },
  },
}
</script>

<style lang="less">
@import '~assets/style/variables.less';
@import '~assets/style/mixins.less';

.CountrySelectorPopper {
  max-width: @advancedSearchWidth - 40px;
}
</style>
