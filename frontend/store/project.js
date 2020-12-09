import Vue from 'vue'
import get from 'lodash/get'
import { apiReadParser, apiWriteParser, APIError } from '../utilities/api'
import { projectFields } from '../utilities/projects'

const cleanState = () => ({
  ...projectFields(),
  country_answers: [],
  donors_answers: [],
  published: null,
  original: null,
})

export const state = () => ({
  ...cleanState(),
  loading: false,
})

export const getters = {
  getProjectData: (state, getters, rootState, rootGetters) => ({
    ...state,
    organisation: rootGetters['system/getUnicefOrganisation'].id,
    donors: getters.getDonors,
    interoperability_links: getters.getInteroperabilityLinks,
    published: undefined,
    loading: undefined,
    country_answers: undefined,
    donor_answers: undefined,
    original: undefined,
  }),
  getName: (state) => state.name,
  getOrganisation: (state) => state.organisation,
  getCountry: (state) => state.country,
  getCountryOffice: (state) => state.country_office,
  getModified: (state) => state.modified,
  getImplementationOverview: (state) => state.implementation_overview,
  getStartDate: (state) => state.start_date,
  getEndDate: (state) => state.end_date,
  getContactName: (state) => state.contact_name,
  getContactEmail: (state) => state.contact_email,
  getTeam: (state) => state.team,
  getViewers: (state) => state.viewers,
  getGoalArea: (state) => state.goal_area,
  getResultArea: (state) => state.result_area,
  getGoalAreaDetails: (state, getters, rootState, rootGetters) => {
    const selected = rootGetters['projects/getGoalAreas'].find(
      (ga) => ga.id === state.goal_area
    )
    return selected || {}
  },
  getCapabilityLevels: (state) => state.capability_levels,
  getCapabilityCategories: (state) => state.capability_categories,
  getCapabilitySubcategories: (state) => state.capability_subcategories,
  getPlatforms: (state) =>
    state.platforms.length === 0 ? [] : state.platforms,
  getSectors: (state) =>
    state.unicef_sector.length === 0 ? [null] : state.unicef_sector,
  getRegionalPriorities: (state) =>
    state.regional_priorities.length === 0 ? [null] : state.regional_priorities,
  getHardware: (state) => (state.hardware.length === 0 ? [] : state.hardware),
  getNontech: (state) => (state.nontech.length === 0 ? [] : state.nontech),
  getFunctions: (state) =>
    state.functions.length === 0 ? [null] : state.functions,
  getInnovationWays: (state) =>
    state.innovation_ways.length === 0 ? [null] : state.innovation_ways,
  getInfoSec: (state) => state.isc,
  getOverview: (state) => state.overview,
  getProgramTargets: (state) => state.program_targets,
  getProgramTargetsAchieved: (state) => state.program_targets_achieved,
  getCurrentAchievements: (state) => state.current_achievements,
  getAwp: (state) => state.awp,
  getPhase: (state) => state.phase,
  getCpd: (state) => state.cpd,
  getInnovationCategories: (state) => state.innovation_categories,
  getLinks: (state) => (state.links.length === 0 ? [null] : state.links),
  getPartners: (state) =>
    state.partners.length === 0 ? [null] : state.partners,
  getWbs: (state) => (state.wbs.length === 0 ? [null] : state.wbs),
  getTargetGroupReached: (state) => state.target_group_reached,
  getCurrency: (state) => state.currency,
  getTotalBudget: (state) => state.total_budget,
  getTotalBudgetNarrative: (state) => state.total_budget_narrative,
  getFundingNeeds: (state) => state.funding_needs,
  getPartnershipNeeds: (state) => state.partnership_needs,
  getDigitalHealthInterventions: (state) => [...state.dhis],
  getHealthFocusAreas: (state) => state.health_focus_areas,
  getHscChallenges: (state) => state.hsc_challenges,
  getDonors: (state, getters, rootState, rootGetters) => {
    const uniCode = rootGetters['system/getUnicefDonor'].id
    const cleaned = state.donors.filter((d) => d !== uniCode)
    return [uniCode, ...cleaned]
  },
  getDonorsAnswers: (state) =>
    state.donors_answers ? [...state.donors_answers] : [],
  getDonorsAnswerDetails: (state, getters) => (id) =>
    getters.getDonorsAnswers.find((da) => da.question_id === id),
  getAllDonorsAnswers: (state, getters, rootState, rootGetters) => {
    const donors = getters.getDonors
      .map((d) => rootGetters['system/getDonorDetails'](d))
      .filter((d) => d.donor_questions)
    if (donors) {
      return donors.reduce((a, c) => {
        a.push(
          ...c.donor_questions.map((dq) => {
            const answer = getters.getDonorsAnswerDetails(dq.id)
            return {
              question_id: dq.id,
              answer: answer ? answer.answer : [],
              donor_id: c.id,
            }
          })
        )
        return a
      }, [])
    }
  },
  getPublishedDonorsAnswerDetails: (state, getters) => (id) => {
    return getters.getPublished.donor_custom_answers.find(
      (ca) => ca.question_id === id
    )
  },

  getPublished: (state) => ({
    ...state.published,
    team: state.team,
    viewers: state.viewers,
  }),
  getLoading: (state) => state.loading,
  getOriginal: (state) => state.original,
}

export const actions = {
  async loadProject({ commit, dispatch, rootGetters }, id) {
    // const unicefId = rootGetters['system/getUnicefOrganisation'].id
    const userProject = rootGetters['projects/getUserProjectList'].find(
      (p) => p.id === id
    )
    const { data } =
      userProject && userProject.id
        ? { data: userProject }
        : await this.$axios.get(`/api/projects/${id}/`)
    commit('SET_ORIGINAL', Object.freeze(data))
    const clean = cleanState()
    const donorsToFetch = new Set([rootGetters['system/getUnicefDonor'].id])
    if (data.draft) {
      const draft = { ...clean, ...apiReadParser(data.draft) }
      draft.donors.forEach((d) => donorsToFetch.add(d))
      commit('INIT_PROJECT', draft)
    }
    if (data.published) {
      const published = { ...clean, ...apiReadParser(data.published) }
      published.donors.forEach((d) => donorsToFetch.add(d))
      commit('SET_PUBLISHED', Object.freeze(published))
    }
    await Promise.all([
      ...[...donorsToFetch].map((df) =>
        dispatch('system/loadDonorDetails', df, { root: true })
      ),
      dispatch('loadTeamViewers', id),
    ])
  },
  async loadTeamViewers({ commit, rootGetters }, projectId) {
    const profile = rootGetters['user/getProfile']
    if (profile) {
      const { data } = await this.$axios.get(
        `/api/projects/${projectId}/groups/`
      )
      commit('SET_TEAM', data.team)
      commit('SET_VIEWERS', data.viewers)
    }
  },
  async resetProjectState({ commit, rootGetters, dispatch }) {
    const clean = cleanState()
    const profile = rootGetters['user/getProfile']
    if (profile) {
      const donor = rootGetters['system/getUnicefDonor'].id
      clean.country = profile.country
      clean.country_office = profile.country_office
      clean.team = [profile.id]
      clean.organisation = rootGetters['system/getUnicefOrganisation'].id
      clean.donors = [donor]
      await Promise.all([
        dispatch('countries/loadCountryDetails', profile.country, {
          root: true,
        }),
        dispatch('system/loadDonorDetails', donor, { root: true }),
      ])
    }
    commit('INIT_PROJECT', clean)
    commit('SET_TEAM', clean.team)
    commit('SET_VIEWERS', clean.viewers)
  },
  initProjectState({ commit }, value) {
    commit('INIT_PROJECT', value)
    commit('SET_TEAM', value.team)
    commit('SET_VIEWERS', value.viewers)
  },
  setGoalArea({ commit }, value) {
    commit('SET_DATA', { key: 'goal_area', value })
    commit('SET_DATA', { key: 'result_area', value: null })
    commit('SET_DATA', { key: 'capability_levels', value: [] })
    commit('SET_DATA', { key: 'capability_categories', value: [] })
    commit('SET_DATA', { key: 'capability_subcategories', value: [] })
  },
  setResultArea({ commit }, value) {
    commit('SET_DATA', { key: 'result_area', value })
  },
  setCapabilityLevels({ commit }, value) {
    commit('SET_DATA', { key: 'capability_levels', value })
  },
  setCapabilityCategories({ commit }, value) {
    commit('SET_DATA', { key: 'capability_categories', value })
  },
  setCapabilitySubcategories({ commit }, value) {
    commit('SET_DATA', { key: 'capability_subcategories', value })
  },
  setName({ commit }, value) {
    commit('SET_NAME', value)
  },
  setOrganisation({ commit }, value) {
    commit('SET_ORGANISATION', value)
  },
  setCountry({ commit, dispatch }, value) {
    dispatch('countries/loadCountryDetails', value, { root: true })
    commit('SET_COUNTRY', value)
  },
  setCountryOffice({ commit, dispatch }, value) {
    dispatch('offices/loadOffice', value, { root: true })
    commit('SET_COUNTRY_OFFICE', value)
  },
  setImplementationOverview({ commit }, value) {
    commit('SET_IMPLEMENTATION_OVERVIEW', value)
  },
  setStartDate({ commit }, value) {
    commit('SET_START_DATE', value)
  },
  setEndDate({ commit }, value) {
    commit('SET_END_DATE', value)
  },
  setContactName({ commit }, value) {
    commit('SET_CONTACT_NAME', value)
  },
  setContactEmail({ commit }, value) {
    commit('SET_CONTACT_EMAIL', value)
  },
  setTeam({ commit }, value) {
    commit('SET_TEAM', value)
  },
  setViewers({ commit }, value) {
    commit('SET_VIEWERS', value)
  },
  setPlatforms({ commit }, value) {
    commit('SET_PLATFORMS', value)
  },
  setSectors({ commit }, value) {
    commit('SET_SECTORS', value)
  },
  setRegionalPriorities({ commit }, value) {
    commit('SET_REGIONAL_PRIORITIES', value)
  },
  setHardware({ commit }, value) {
    commit('SET_HARDWARE', value)
  },
  setNontech({ commit }, value) {
    commit('SET_NONTECH', value)
  },
  setFunctions({ commit }, value) {
    commit('SET_FUNCTIONS', value)
  },
  setInfoSec({ commit }, value) {
    commit('SET_DATA', { key: 'isc', value })
  },
  setInnovationWays({ commit }, value) {
    commit('SET_DATA', { key: 'innovation_ways', value })
  },
  setOverview({ commit }, value) {
    commit('SET_DATA', { key: 'overview', value })
  },
  setPartnershipNeeds({ commit }, value) {
    commit('SET_DATA', { key: 'partnership_needs', value })
  },
  setFundingNeeds({ commit }, value) {
    commit('SET_DATA', { key: 'funding_needs', value })
  },
  setTotalBudgetNarrative({ commit }, value) {
    commit('SET_DATA', { key: 'total_budget_narrative', value })
  },
  setAwp({ commit }, value) {
    commit('SET_DATA', { key: 'awp', value })
  },
  setPhase({ commit }, value) {
    commit('SET_DATA', { key: 'phase', value })
  },
  setCpd({ commit }, value) {
    commit('SET_DATA', { key: 'cpd', value })
  },
  setInnovationCategories({ commit }, value) {
    commit('SET_DATA', { key: 'innovation_categories', value })
  },
  setLinks({ commit }, value) {
    commit('SET_DATA', { key: 'links', value })
  },
  setPartners({ commit }, value) {
    commit('SET_DATA', { key: 'partners', value })
  },
  setWbs({ commit }, value) {
    commit('SET_DATA', { key: 'wbs', value })
  },
  setTargetGroupReached({ commit }, value) {
    commit('SET_DATA', { key: 'target_group_reached', value })
  },
  setCurrency({ commit }, value) {
    commit('SET_DATA', { key: 'currency', value })
  },
  setTotalBudget({ commit }, value) {
    commit('SET_DATA', { key: 'total_budget', value })
  },
  setCurrentAchievements({ commit }, value) {
    commit('SET_DATA', { key: 'current_achievements', value })
  },
  setProgramTargetsAchieved({ commit }, value) {
    commit('SET_DATA', { key: 'program_targets_achieved', value })
  },
  setProgramTargets({ commit }, value) {
    commit('SET_DATA', { key: 'program_targets', value })
  },
  setDigitalHealthInterventions({ commit }, value) {
    commit('SET_DIGITAL_HEALTH_INTERVENTIONS', value)
  },
  setHealthFocusAreas({ commit }, value) {
    commit('SET_HEALTH_FOCUS_AREAS', value)
  },
  setHscChallenges({ commit }, value) {
    commit('SET_HSC_CHALLENGES', value)
  },
  setDonors({ commit, dispatch }, value) {
    value.forEach((d) => dispatch('system/loadDonorDetails', d, { root: true }))
    commit('SET_DONORS', value)
  },
  setImplementationDates({ commit }, value) {
    commit('SET_IMPLEMENTATION_DATES', value)
  },
  setPublished({ commit }, value) {
    commit('SET_PUBLISHED', value)
  },
  setLoading({ commit }, value) {
    commit('SET_LOADING', value)
  },
  setDonorAnswer({ commit, getters }, answer) {
    const index = getters.getDonorsAnswers.findIndex(
      (da) => da.question_id === answer.question_id
    )
    if (index > -1) {
      commit('UPDATE_DONOR_ANSWER', { answer, index })
    } else {
      commit('ADD_DONOR_ANSWER', answer)
    }
  },
  async verifyOrganisation({ dispatch }, organisation) {
    try {
      if (organisation && isNaN(organisation)) {
        const org = await dispatch('system/addOrganisation', organisation, {
          root: true,
        })
        return org.id
      }
      return organisation
    } catch (e) {
      console.log('project/verifyOrganisation failed')
      return Promise.reject(
        APIError('organisation', 'Failed to save the organisation')
      )
    }
  },
  async saveTeamViewers({ getters, commit, dispatch }, id) {
    const teamViewers = {
      team: getters.getTeam.filter((d) => typeof d === 'number'),
      viewers: getters.getViewers.filter((d) => typeof d === 'number'),
      new_team_emails: getters.getTeam.filter((d) => typeof d === 'string'),
      new_viewer_emails: getters.getViewers.filter(
        (d) => typeof d === 'string'
      ),
    }
    const { data } = await this.$axios.put(
      `/api/projects/${id}/groups/`,
      teamViewers
    )
    commit('SET_TEAM', data.team)
    commit('SET_VIEWERS', data.viewers)
    return dispatch('user/updateTeamViewers', { ...data, id }, { root: true })
  },
  async createProject({ state, getters, dispatch, rootGetters }) {
    dispatch('setLoading', 'draft')
    const draft = getters.getProjectData
    draft.organisation = rootGetters['system/getUnicefOrganisation'].id
    draft.donors = [rootGetters['system/getUnicefDonor'].id]
    const parsed = apiWriteParser(
      draft,
      getters.getAllCountryAnswers,
      getters.getAllDonorsAnswers
    )
    const { data } = await this.$axios.post(
      `api/projects/draft/${draft.country_office}/`,
      parsed
    )
    dispatch('projects/addProjectToList', data, { root: true })
    await dispatch('saveTeamViewers', data.id)
    dispatch('setLoading', false)
    return data.id
  },
  async saveDraft({ state, getters, dispatch, rootGetters }, id) {
    dispatch('setLoading', 'draft')
    const draft = getters.getProjectData
    draft.organisation = rootGetters['system/getUnicefOrganisation'].id
    draft.donors = [rootGetters['system/getUnicefDonor'].id]
    const parsed = apiWriteParser(
      draft,
      getters.getAllCountryAnswers,
      getters.getAllDonorsAnswers
    )
    const { data } = await this.$axios.put(
      `api/projects/draft/${id}/${draft.country_office}/`,
      parsed
    )
    await dispatch('setProject', { data, id })
    dispatch('setLoading', false)
  },
  async publishProject({ getters, dispatch, commit, rootGetters }, id) {
    dispatch('setLoading', 'publish')
    const draft = getters.getProjectData
    draft.organisation = rootGetters['system/getUnicefOrganisation'].id
    draft.donors = [rootGetters['system/getUnicefDonor'].id]
    const parsed = apiWriteParser(
      draft,
      getters.getAllCountryAnswers,
      getters.getAllDonorsAnswers
    )
    const { data } = await this.$axios.put(
      `/api/projects/publish/${id}/${draft.country_office}/`,
      parsed
    )
    const parsedResponse = apiReadParser(data.draft)
    commit('SET_PUBLISHED', Object.freeze(parsedResponse))
    await dispatch('setProject', { data, id })
    dispatch('setLoading', false)
  },
  async unpublishProject({ dispatch }, id) {
    dispatch('setLoading', 'unpublish')
    const { data } = await this.$axios.put(`/api/projects/unpublish/${id}/`)
    await dispatch('setProject', { data, id })
    dispatch('setLoading', false)
  },
  async latestProject({ dispatch }, id) {
    dispatch('setLoading', 'latest')
    const { data } = await this.$axios.get(
      `/api/projects/publishaslatest/${id}/`
    )
    await dispatch('setProject', { data, id })
    dispatch('setLoading', false)
  },
  async setProject({ dispatch }, { data, id }) {
    const isUserProject = await dispatch('saveTeamViewers', id)
    if (isUserProject) {
      dispatch('projects/updateProject', data, { root: true })
    } else {
      dispatch('projects/removeProject', data.id, { root: true })
    }
  },
  async discardDraft({ getters, dispatch, commit }, id) {
    dispatch('setLoading', 'discard')
    const published = getters.getPublished
    const parsed = apiWriteParser(
      published,
      published.country_custom_answers,
      published.donor_custom_answers
    )
    const { data } = await this.$axios.put(
      `api/projects/draft/${id}/${published.country_office}/`,
      parsed
    )
    const parsedResponse = apiReadParser(data.draft)
    commit('INIT_PROJECT', parsedResponse)
    dispatch('projects/updateProject', data, { root: true })
    dispatch('setLoading', false)
  },
}

export const mutations = {
  SET_DATA: (state, { value, key }) => {
    state[key] = value
  },
  SET_NAME: (state, name) => {
    state.name = name
  },
  SET_ORGANISATION: (state, organisation) => {
    state.organisation = organisation
  },
  SET_COUNTRY: (state, country) => {
    state.country = country
  },
  SET_COUNTRY_OFFICE: (state, office) => {
    state.country_office = office
  },
  SET_IMPLEMENTATION_OVERVIEW: (state, implementation_overview) => {
    state.implementation_overview = implementation_overview
  },
  SET_START_DATE: (state, start_date) => {
    state.start_date = start_date
  },
  SET_END_DATE: (state, end_date) => {
    state.end_date = end_date
  },
  SET_CONTACT_NAME: (state, contact_name) => {
    state.contact_name = contact_name
  },
  SET_CONTACT_EMAIL: (state, contact_email) => {
    state.contact_email = contact_email
  },
  SET_TEAM: (state, team) => {
    const items = typeof team === 'string' ? state.team.concat([team]) : team
    Vue.set(state, 'team', [...items])
  },
  SET_VIEWERS: (state, viewer) => {
    const items =
      typeof viewer === 'string' ? state.viewers.concat([viewer]) : viewer
    Vue.set(state, 'viewers', [...items])
  },
  SET_PLATFORMS: (state, platforms) => {
    Vue.set(state, 'platforms', [...platforms])
  },
  SET_SECTORS: (state, unicef_sector) => {
    Vue.set(state, 'unicef_sector', [...unicef_sector])
  },
  SET_REGIONAL_PRIORITIES: (state, regional_priorities) => {
    Vue.set(state, 'regional_priorities', [...regional_priorities])
  },
  SET_HARDWARE: (state, hardware) => {
    Vue.set(state, 'hardware', [...hardware])
  },
  SET_NONTECH: (state, nontech) => {
    Vue.set(state, 'nontech', [...nontech])
  },
  SET_FUNCTIONS: (state, functions) => {
    Vue.set(state, 'functions', [...functions])
  },
  SET_DIGITAL_HEALTH_INTERVENTIONS: (state, dhi) => {
    Vue.set(state, 'dhis', [...dhi])
  },
  SET_HEALTH_FOCUS_AREAS: (state, health_focus_areas) => {
    Vue.set(state, 'health_focus_areas', [...health_focus_areas])
  },
  SET_HSC_CHALLENGES: (state, hsc_challenges) => {
    Vue.set(state, 'hsc_challenges', [...hsc_challenges])
  },
  SET_DONORS: (state, donors) => {
    Vue.set(state, 'donors', [...donors])
  },
  SET_IMPLEMENTATION_DATES: (state, implementation_dates) => {
    state.implementation_dates = implementation_dates
  },
  ADD_DONOR_ANSWER: (state, answer) => {
    state.donors_answers.push(answer)
  },
  UPDATE_DONOR_ANSWER: (state, { answer, index }) => {
    state.donors_answers.splice(index, 1, answer)
  },
  SET_PUBLISHED: (state, published) => {
    Vue.set(state, 'published', { ...published })
  },
  SET_LOADING: (state, loading) => {
    state.loading = loading
  },
  INIT_PROJECT: (state, project) => {
    state.name = get(project, 'name', '')
    state.organisation = get(project, 'organisation', null)
    state.country = get(project, 'country', null)
    state.country_office = get(project, 'country_office', null)
    state.modified = get(project, 'modified', null)
    state.implementation_overview = get(project, 'implementation_overview', '')
    state.start_date = get(project, 'start_date', '')
    state.end_date = get(project, 'end_date', '')
    state.contact_name = get(project, 'contact_name', '')
    state.contact_email = get(project, 'contact_email', '')
    state.team = get(project, 'team', [])
    state.viewers = get(project, 'viewers', [])
    state.goal_area = get(project, 'goal_area', null)
    state.result_area = get(project, 'result_area', null)
    state.capability_levels = get(project, 'capability_levels', [])
    state.capability_categories = get(project, 'capability_categories', [])
    state.capability_subcategories = get(
      project,
      'capability_subcategories',
      []
    )
    state.platforms = get(project, 'platforms', [])
    state.dhis = get(project, 'dhis', [])
    state.health_focus_areas = get(project, 'health_focus_areas', [])
    state.hsc_challenges = get(project, 'hsc_challenges', [])
    state.modified = get(project, 'modified', new Date())
    state.donors = get(project, 'donors', [])
    state.country_answers = get(project, 'country_custom_answers', [])
    state.donors_answers = get(project, 'donor_custom_answers', [])
    // INVENT
    state.unicef_sector = get(project, 'unicef_sector', [])
    state.functions = get(project, 'functions', [])
    state.hardware = get(project, 'hardware', [])
    state.nontech = get(project, 'nontech', [])
    state.regional_priorities = get(project, 'regional_priorities', [])
    state.overview = get(project, 'overview', '')
    state.program_targets = get(project, 'program_targets', '')
    state.program_targets_achieved = get(
      project,
      'program_targets_achieved',
      ''
    )
    state.current_achievements = get(project, 'current_achievements', '')
    state.awp = get(project, 'awp', '')
    state.total_budget_narrative = get(project, 'total_budget_narrative', '')
    state.funding_needs = get(project, 'funding_needs', '')
    state.partnership_needs = get(project, 'partnership_needs', '')
    state.target_group_reached = get(project, 'target_group_reached', '')
    state.currency = get(project, 'currency', 1)
    state.total_budget = get(project, 'total_budget', '')
    state.wbs = get(project, 'wbs', [])
    state.innovation_categories = get(project, 'innovation_categories', [])
    state.links = get(project, 'links', [])
    state.cpd = get(project, 'cpd', [])
    state.partners = get(project, 'partners', [])
    state.phase = get(project, 'phase', null)
    state.isc = get(project, 'isc', null)
    state.innovation_ways = get(project, 'innovation_ways', [])
  },
  SET_ORIGINAL: (state, project) => {
    state.original = project
  },
}
