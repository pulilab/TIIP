<template>
  <div id="implementation" class="ImplementationOverview">
    <collapsible-card
      ref="collapsible"
      :title="$gettext('Implementation overview') | translate"
      show-legend
    >
      <custom-required-form-item
        :error="errors.first('program_targets')"
        :draft-rule="draftRules.program_targets"
        :publish-rule="publishRules.program_targets"
      >
        <template slot="label">
          <translate key="program_targets">
            What are the final programme targets the initiative aims to achieve?
          </translate>
        </template>

        <character-count-input
          v-model="program_targets"
          v-validate="rules.program_targets"
          :rules="rules.program_targets"
          data-vv-name="program_targets"
          data-vv-as="Program Targets"
          type="textarea"
        />
        <span class="Hint">
          <fa icon="info-circle" />
          <p>
            <translate>
              Programme targets and metrics refer to quantitative or qualitative
              measures of how to assess initiative achievement and outputs for a
              certain period of time. Good metrics help track initiative
              progress and promote strategic analysis for continuous
              improvement. eg. percentage of geographic coverage.
            </translate>
          </p>
        </span>
      </custom-required-form-item>

      <custom-required-form-item
        :error="errors.first('program_targets_achieved')"
        :draft-rule="draftRules.program_targets_achieved"
        :publish-rule="publishRules.program_targets_achieved"
      >
        <template slot="label">
          <translate key="program_targets_achieved">
            What are the programme targets the initiative has achieved to date?
          </translate>
        </template>

        <character-count-input
          v-model="program_targets_achieved"
          v-validate="rules.program_targets_achieved"
          :rules="rules.program_targets_achieved"
          data-vv-name="program_targets_achieved"
          data-vv-as="Program Targets Achieved"
          type="textarea"
        />
        <span class="Hint">
          <fa icon="info-circle" />
          <p>
            <translate>
              Provide a snapshot of any targets already achieved at the time of
              this update.
            </translate>
          </p>
        </span>
      </custom-required-form-item>

      <custom-required-form-item
        :error="errors.first('target_group_reached')"
        :draft-rule="draftRules.target_group_reached"
        :publish-rule="publishRules.target_group_reached"
      >
        <template slot="label">
          <translate key="target_group_reached">
            How many beneficiaries are reached by the initiative?
          </translate>
        </template>

        <el-input-number
          v-model="target_group_reached"
          v-validate="rules.target_group_reached"
          data-vv-name="target_group_reached"
          data-vv-as="Target Group"
          controls-position="right"
          :min="0"
          class="number-input"
        />
        <span class="Hint">
          <fa icon="info-circle" />
          <p>
            <translate>
              This refers to the scale of defined target groups that are
              receiving benefits from the initiative.
            </translate>
          </p>
        </span>
      </custom-required-form-item>

      <custom-required-form-item
        :error="errors.first('current_achievements')"
        :draft-rule="draftRules.current_achievements"
        :publish-rule="publishRules.current_achievements"
      >
        <template slot="label">
          <translate key="current_achievements">
            What impact has the initiative had to date?
          </translate>
        </template>

        <character-count-input
          v-model="current_achievements"
          v-validate="rules.current_achievements"
          :rules="rules.current_achievements"
          data-vv-name="current_achievements"
          data-vv-as="Current Achievements"
          type="textarea"
        />
        <span class="Hint">
          <fa icon="info-circle" />
          <p>
            <translate>
              Please provide information about the realisation of the
              initiative's objectives at the time of entry. This could include
              the number of target populations reached, partnerships, funding
              secured, spin-off initiatives, etc.
            </translate>
          </p>
        </span>
      </custom-required-form-item>

      <custom-required-form-item
        :error="errors.first('cpd')"
        :draft-rule="draftRules.cpd"
        :publish-rule="publishRules.cpd"
      >
        <template slot="label">
          <translate key="cpd-label">
            Is the initiative included in the Country Programme Document and
            Annual Work Plan?
          </translate>
        </template>

        <multi-selector
          v-model="cpd"
          v-validate="rules.cpd"
          data-vv-name="cpd"
          data-vv-as="In Country programme document (CPD) and annual work plan"
          source="getCpd"
        />
        <span class="Hint">
          <fa icon="info-circle" />
          <p>
            <translate>
              Country programme document (CPD) is a description of the outcomes,
              outputs and strategies to be adopted in a proposed country
              programme of cooperation submitted to the UNICEF Executive Board
              together with a summary results matrix. The Annual work plan is
              tied to the CPD and describes the specific activities to be
              supported by UNICEF during a particular year in order to achieve
              the results specified in its CPD.
            </translate>
          </p>
        </span>
      </custom-required-form-item>

      <custom-required-form-item
        :error="errors.first('awp')"
        :draft-rule="draftRules.awp"
        :publish-rule="publishRules.awp"
      >
        <template slot="label">
          <translate key="awp">
            Please input which outcomes or activities the initiative serves in
            the Annual Work Plan.
          </translate>
        </template>

        <character-count-input
          v-model="awp"
          v-validate="rules.awp"
          :rules="rules.awp"
          data-vv-name="awp"
          data-vv-as="Annual Work Plan"
          type="textarea"
        />
        <span class="Hint">
          <fa icon="info-circle" />
          <p>
            <translate>
              This refers to the activities and associated information
              (timeframe, budget, responsibilities) in the annual work plan to
              achieve the results specified in its CPD.
            </translate>
          </p>
        </span>
      </custom-required-form-item>

      <el-row v-for="(wbsItem, index) in wbs" :key="index">
        <el-col :span="16">
          <custom-required-form-item
            :error="errors.first('wbs')"
            :draft-rule="draftRules.wbs"
            :publish-rule="publishRules.wbs"
          >
            <template slot="label">
              <translate key="wbs">
                Please enter the Work Breakdown Structure (WBS) number for the
                initiative.
              </translate>
            </template>
            <template slot="tooltip">
              <el-tooltip
                class="item"
                content="WBS format:  nnnn/an/nn/nnn/nnn/nnn where n is a number; a is an alphanumeric character"
                placement="right"
              >
                <i class="el-icon-warning warning" />
              </el-tooltip>
            </template>

            <character-count-input
              v-validate="rules.wbs"
              :value="wbsItem"
              :rules="rules.wbs"
              data-vv-name="wbs"
              data-vv-as="Work Breakdown Structure (WBS)"
              @input="setWbsItem(index, $event)"
            />
            <span class="Hint">
              <fa icon="info-circle" />
              <p>
                <translate>
                  Enter the Work Breakdown Structure (WBS) code(s) at the
                  activity level. The WBS provides the foundation for programme
                  planning, budget planning and resource allocation. It consists
                  of WBS Elements, which describe tasks or subtasks to be
                  performed within a defined time period. You can add more than
                  one WBS number by clicking on the ‘+’ option. For more info:
                  https://uni.cf/invent-help
                </translate>
              </p>
            </span>
          </custom-required-form-item>
        </el-col>
        <el-col :span="8" class="btContainer">
          <add-rm-buttons
            :show-add="isLastAndExist(wbs, index)"
            :show-rm="wbs.length > 1"
            @add="addDhi"
            @rm="rmDhi(index)"
          />
        </el-col>
      </el-row>

      <el-row>
        <el-col :span="16" class="BudgetSection">
          <custom-required-form-item
            :error="errors.first('total_budget')"
            :draft-rule="draftRules.total_budget"
            :publish-rule="publishRules.total_budget"
          >
            <template slot="label">
              <translate key="total_budget">
                What is the total estimated budget for the initiative?
              </translate>
            </template>
            <el-input-number
              v-model="total_budget"
              v-validate="rules.total_budget"
              data-vv-name="total_budget"
              data-vv-as="Total Budget"
              controls-position="right"
              :min="0"
              class="number-input"
            />
            <span class="Hint">
              <fa icon="info-circle" />
              <p>
                <translate>
                  The total estimated budget from ideation through to handover.
                </translate>
              </p>
            </span>
          </custom-required-form-item>
        </el-col>
        <el-col :span="8">
          <custom-required-form-item
            v-if="total_budget"
            :error="errors.first('currency')"
            :draft-rule="draftRules.currency"
            :publish-rule="publishRules.currency"
          >
            <template slot="label">
              <translate key="currency-label"> Currency </translate>
            </template>

            <single-select
              v-model="currency"
              v-validate="rules.currency"
              data-vv-name="currency"
              data-vv-as="Currency"
              source="projects/getCurrencies"
            />
          </custom-required-form-item>
        </el-col>
      </el-row>

      <custom-required-form-item
        :error="errors.first('total_budget_narrative')"
        :draft-rule="draftRules.total_budget_narrative"
        :publish-rule="publishRules.total_budget_narrative"
      >
        <template slot="label">
          <translate key="total_budget_narrative">
            Please explain briefly the main activities covered by the budget.
          </translate>
        </template>

        <character-count-input
          v-model="total_budget_narrative"
          v-validate="rules.total_budget_narrative"
          :rules="rules.total_budget_narrative"
          data-vv-name="total_budget_narrative"
          data-vv-as="Total Budget Narrative"
          type="textarea"
        />
      </custom-required-form-item>

      <custom-required-form-item
        :error="errors.first('funding_needs')"
        :draft-rule="draftRules.funding_needs"
        :publish-rule="publishRules.funding_needs"
      >
        <template slot="label">
          <translate key="funding_needs">
            What are the funding needs to achieve the objectives of the
            initiative?
          </translate>
        </template>

        <character-count-input
          v-model="funding_needs"
          v-validate="rules.funding_needs"
          :rules="rules.funding_needs"
          data-vv-name="funding_needs"
          data-vv-as="Funding Needs"
          type="textarea"
        />

        <span class="Hint">
          <fa icon="info-circle" />
          <p>
            <translate>
              Please provide an indication of the funding gaps.
            </translate>
          </p>
        </span>
      </custom-required-form-item>

      <custom-required-form-item
        :error="errors.first('partnership_needs')"
        :draft-rule="draftRules.partnership_needs"
        :publish-rule="publishRules.partnership_needs"
      >
        <template slot="label">
          <translate key="partnership_needs">
            What partnerships are needed for this initiative?
          </translate>
        </template>
        <character-count-input
          v-model="partnership_needs"
          v-validate="rules.partnership_needs"
          :rules="rules.partnership_needs"
          data-vv-name="partnership_needs"
          data-vv-as="Partnership Needs"
          type="textarea"
        />

        <span class="Hint">
          <fa icon="info-circle" />
          <p>
            <translate>
              Please be as specific as possible about the partnership needs.
              They could be NGO, academic, financial, private, etc.
            </translate>
          </p>
        </span>
      </custom-required-form-item>

      <div class="el-form-item">
        <label class="el-form-item__label">
          <translate> Links to website/Current Documentation </translate>
        </label>
        <el-row v-for="(link, index) in links" :key="`Link_${index}`">
          <el-col :span="16">
            <single-select
              :value="link ? link.link_type : null"
              data-vv-name="linkType"
              data-vv-as="Link Type"
              source="system/getLinkTypes"
              @change="setLinkItem(index, 'link_type', $event)"
            />
          </el-col>
          <el-col :span="8">
            <add-rm-buttons
              :show-add="isLastAndExist(links, index)"
              :show-rm="links.length > 1"
              @add="addLink"
              @rm="rmLink(index)"
            />
          </el-col>
          <el-col v-if="link" :span="24">
            <custom-required-form-item
              :error="errors.first('link_website' + index)"
              :draft-rule="draftRules.link_website"
              :publish-rule="publishRules.link_website"
            >
              <template slot="tooltip">
                <el-tooltip
                  class="item"
                  content="URL format: https://invent.unicef.org"
                  placement="right"
                >
                  <i class="el-icon-warning warning" />
                </el-tooltip>
              </template>
              <character-count-input
                v-validate="rules.link_website"
                :value="link.link_url"
                :rules="rules.link_website"
                :data-vv-name="'link_website' + index"
                data-vv-as="Link Website"
                @input="setLinkItem(index, 'link_url', $event)"
              />
              <span class="Hint">
                <fa icon="info-circle" />
                <p v-show="link.link_type === 0">
                  <translate>
                    Provide a link to the main website for the initiative, if
                    applicable.
                  </translate>
                </p>
                <p v-show="link.link_type === 1">
                  <translate>
                    Provide the link(s) to the Sharepoint or other repository
                    holding all the relevant documentation for the initiative.
                  </translate>
                </p>
                <p v-show="link.link_type === 2">
                  <translate>
                    Provide link(s) to any advocacy and marketing stories
                    celebrating the initiative.
                  </translate>
                </p>
                <p v-show="link.link_type === 3">
                  <translate>
                    Provide link(s) to any research and or reports detailing
                    monitoring, evaluation or learning associated with the
                    initiative.
                  </translate>
                </p>
                <p v-show="link.link_type === 4">
                  <translate>
                    Provide any other link(s) associated with the initiative.
                  </translate>
                </p>
              </span>
            </custom-required-form-item>
          </el-col>
        </el-row>
      </div>
    </collapsible-card>
  </div>
</template>

<script>
import { mapGettersActions } from '@/utilities/form'
import SingleSelect from '@/components/common/SingleSelect'
import MultiSelector from '@/components/project/MultiSelector'
import AddRmButtons from '@/components/project/AddRmButtons'
import CollapsibleCard from '@/components/project/CollapsibleCard'
import VeeValidationMixin from '@/components/mixins/VeeValidationMixin.js'
import ProjectFieldsetMixin from '@/components/mixins/ProjectFieldsetMixin.js'

export default {
  components: {
    CollapsibleCard,
    AddRmButtons,
    MultiSelector,
    SingleSelect, // ,
    // DigitalHealthInterventionsSelector,
    // DonorSelector,
    // FormHint
  },
  mixins: [VeeValidationMixin, ProjectFieldsetMixin],

  computed: {
    ...mapGettersActions({
      program_targets: ['project', 'getProgramTargets', 'setProgramTargets', 0],
      program_targets_achieved: [
        'project',
        'getProgramTargetsAchieved',
        'setProgramTargetsAchieved',
        0,
      ],
      current_achievements: [
        'project',
        'getCurrentAchievements',
        'setCurrentAchievements',
        0,
      ],
      awp: ['project', 'getAwp', 'setAwp', 0],
      cpd: ['project', 'getCpd', 'setCpd', 0],
      total_budget_narrative: [
        'project',
        'getTotalBudgetNarrative',
        'setTotalBudgetNarrative',
        0,
      ],
      funding_needs: ['project', 'getFundingNeeds', 'setFundingNeeds', 0],
      partnership_needs: [
        'project',
        'getPartnershipNeeds',
        'setPartnershipNeeds',
        0,
      ],
      target_group_reached: [
        'project',
        'getTargetGroupReached',
        'setTargetGroupReached',
        0,
      ],
      currency: ['project', 'getCurrency', 'setCurrency', 0],
      total_budget: ['project', 'getTotalBudget', 'setTotalBudget', 0],
      links: ['project', 'getLinks', 'setLinks', 0],
      wbs: ['project', 'getWbs', 'setWbs', 0],
      // digitalHealthInterventions: [
      //   'project',
      //   'getDigitalHealthInterventions',
      //   'setDigitalHealthInterventions',
      //   0,
      // ],
      // donors: ['project', 'getDonors', 'setDonors', 0],
    }),
  },
  methods: {
    async validate() {
      this.$refs.collapsible.expandCard()
      const validations = await Promise.all([this.$validator.validate()])
      console.log('Implementation overview validations', validations)
      return validations.reduce((a, c) => a && c, true)
    },
    isLastAndExist(collection, index) {
      return !!(collection.length - 1 === index && collection[index])
    },
    addDhi() {
      this.wbs = [...this.wbs, null]
    },
    rmDhi(index) {
      this.wbs = this.wbs.filter((p, i) => i !== index)
    },
    setWbsItem(index, value) {
      const wbs = [...this.wbs]
      wbs[index] = value
      this.wbs = wbs
    },
    addLink() {
      this.links = [...this.links, null]
    },
    rmLink(index) {
      this.links = this.links.filter((p, i) => i !== index)
    },
    setLinkItem(index, key, value) {
      const links = [...this.links]
      links[index] = links[index] ? { ...links[index] } : {}
      links[index][key] = value
      this.links = links
    },
  },
}
</script>

<style lang="less">
@import '~assets/style/variables.less';
@import '~assets/style/mixins.less';

.ImplementationOverview {
  .DigitalHealthIntervention {
    margin-top: 30px;
  }

  .CoverageArea {
    .CoverageSubtitle {
      position: relative;
      display: block;
      margin: 0 0 20px;
      padding: 10px 0 0 20px;
      font-size: @fontSizeSmall;
      font-weight: 700;
      color: @colorGray;
      text-transform: uppercase;

      .svg-inline--fa {
        position: absolute;
        top: 10px;
        left: 0;
      }
    }
  }
  .BudgetSection {
    padding-right: 15px;
  }
  .btContainer {
    margin-top: 50px;
  }
  .number-input {
    width: 100%;
    &.el-input-number .el-input__inner {
      text-align: left;
    }
  }
}
</style>
