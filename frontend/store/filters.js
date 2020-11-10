import { objectToQueryString, queryStringToObject } from '@/utilities/search'

export const state = () => ({
  tabs: false,
  currentFilter: undefined,
  filters: {},
})

export const actions = {
  async getFilters({ state, commit, dispatch, rootState }) {
    try {
      const {
        data: { filters },
      } = await this.$axios.get(
        `/api/userprofiles/${rootState.user.profile.id}/`
      )
      commit('SET_VALUE', { key: 'filters', val: filters })
    } catch (e) {
      console.error('get filters failed')
    }
  },
  setCurrentFilter({ state, commit, dispatch }, val = undefined) {
    commit('SET_VALUE', { key: 'currentFilter', val })
  },
  setFilters({ state, commit, dispatch }, name) {
    commit('SET_VALUE', { key: 'currentFilter', val: name })
    if (state.tabs) {
      console.log('tabs')
    } else {
      dispatch(
        'dashboard/setSearchOptions',
        queryStringToObject(state.filters[name]),
        {
          root: true,
        }
      )
    }
  },
  async newFilter({ state, dispatch, rootState, rootGetters }, name) {
    const newFilter = {
      [name]: state.tabs
        ? objectToQueryString(rootState.search.filter)
        : objectToQueryString(rootGetters['dashboard/getSearchParameters']),
    }
    await dispatch('updateFilter', {
      ...state.filters,
      ...newFilter,
    })
    await dispatch('setFilters', name)
  },
  async deleteFilter({ state, dispatch }, name = '') {
    const filters = state.filters
    delete filters[name]
    await dispatch('updateFilter', filters)
    if (name === state.currentFilter) {
      await dispatch('setFilters', undefined)
    }
  },
  async updateFilter({ state, commit, dispatch, rootState }, updateFilters) {
    try {
      const {
        data: { filters },
      } = await this.$axios.patch(
        `/api/userprofiles/${rootState.user.profile.id}/`,
        {
          filters: updateFilters,
        }
      )
      commit('SET_VALUE', { key: 'filters', val: filters })
    } catch (e) {
      console.error('update filter failed')
    }
  },
  resetFilters({ state, commit, dispatch }) {
    if (state.tabs) {
      dispatch('search/resetSearch', {}, { root: true })
    } else {
      dispatch('dashboard/resetUserInput', {}, { root: true })
    }
  },
}
export const mutations = {
  SET_VALUE(state, { key, val }) {
    state[key] = val
  },
}
