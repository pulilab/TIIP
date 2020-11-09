export const state = () => ({
  tabs: false,
  currentFilter: undefined,
  filters: [],
})

export const getters = {
  getSearched: (state, getters) => {
    const g = getters.getSearchParameters
    return !(
      g.approved === undefined &&
      g.country.length === 0 &&
      g.dhi.length === 0 &&
      g.donor === null &&
      g.gov === undefined &&
      g.hfa.length === 0 &&
      g.goal === undefined &&
      g.result === undefined &&
      g.cl.length === 0 &&
      g.cc.length === 0 &&
      g.cs.length === 0 &&
      g.hsc.length === 0 &&
      g.ic.length === 0 &&
      g.in === undefined &&
      g.q === undefined &&
      g.region === null &&
      g.fo === null &&
      g.co === null &&
      g.sw.length === 0 &&
      g.view_as === undefined
    )
  },
}

export const actions = {
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
