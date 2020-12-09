<template>
  <lazy-el-select
    :value="platforms"
    multiple
    filterable
    :disabled="disabled"
    :placeholder="placeholder || $gettext('Select from list') | translate"
    popper-class="PlatformSelectorDropdown"
    class="PlatformSelector"
    value-key="id"
    @change="changeHandler"
    @blur="$emit('blur')"
  >
    <el-option
      v-for="platform in filteredList"
      :key="platform.id"
      :label="platform.name"
      :value="platform.id"
    />
  </lazy-el-select>
</template>

<script>
export default {
  name: 'MultiSelector',
  model: {
    prop: 'platforms',
    event: 'change',
  },
  $_veeValidate: {
    value() {
      return this.platform
    },
  },
  props: {
    platforms: {
      type: Array,
      default: () => [],
    },
    source: {
      type: String,
      required: true,
    },
    placeholder: {
      type: String,
      default: '',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    filter: {
      type: Array,
      default: null,
    },
  },
  computed: {
    sourceList() {
      return this.$store.getters['projects/' + this.source]
    },
    filteredList() {
      if (this.filter === null) {
        return this.sourceList
      }
      return this.sourceList.filter(({ id }) => this.filter.includes(id))
    },
  },
  watch: {
    filter(newFilter) {
      if (!this.platforms) {
        return
      }
      this.changeHandler(
        this.platforms.filter((value) => (newFilter || []).includes(value))
      )
    },
  },
  methods: {
    changeHandler(value) {
      this.$emit('change', value)
    },
  },
}
</script>

<style lang="less">
//@import "../../assets/style/variables.less";
//@import "../../assets/style/mixins.less";

.PlatformSelector {
  width: 100%;
}
</style>
