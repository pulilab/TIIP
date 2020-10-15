import map from 'lodash/map'
import find from 'lodash/find'

export const state = {
  ambitionMatrix: [],
  riskImpactMatrix: [],
  problemStatementMatrix: [],
  projects: [],
}

export const actions = {
  async getPortfolioMatrix({ commit }, id) {
    const { data } = await this.$axios.get(
      `/api/search/?portfolio=${id}&portfolio_page=portfolio&type=portfolio&scores`
    )
    const {
      ambition_matrix,
      risk_impact_matrix,
      problem_statement_matrix,
      projects,
    } = data.results
    commit('SET_VALUE', { key: 'ambitionMatrix', val: ambition_matrix })
    commit('SET_VALUE', { key: 'riskImpactMatrix', val: risk_impact_matrix })
    commit('SET_VALUE', {
      key: 'problemStatementMatrix',
      val: problem_statement_matrix,
    })
    commit('SET_VALUE', { key: 'projects', val: projects })
  },
}

function processMatrix(matrix, projects) {
  return map(matrix, function (element) {
    return {
      ...element,
      projects: map(element.projects, function (projectId) {
        const project = find(projects, ({ id }) => projectId)
        return {
          id: projectId,
          title: project.name,
        }
      }),
    }
  })
}

export const getters = {
  getAmbitionMatrix(state) {
    return processMatrix(state.ambitionMatrix, state.projects)
  },
  getRiskImpactMatrix(state) {
    return processMatrix(state.riskImpactMatrix, state.projects)
  },
  getProblemStatementMatrix(state, getters, rootState) {
    const { problemStatements } = rootState.portfolio
    const { neglected, moderate, high_activity } = state.problemStatementMatrix
    return [
      processProblemStatement(neglected, problemStatements),
      processProblemStatement(moderate, problemStatements),
      processProblemStatement(high_activity, problemStatements),
    ]
  },
}

function processProblemStatement(list, statements) {
  return map(list, function (statementId) {
    const statement = find(statements, ({ id }) => id === statementId)
    return {
      id: statementId,
      title: statement.name,
      description: statement.description,
    }
  })
}

export const mutations = {
  SET_VALUE(state, { key, val }) {
    state[key] = val
  },
}
