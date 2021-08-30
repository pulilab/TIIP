<template>
  <el-dialog
    v-if="visible"
    :visible.sync="visible"
    :title="$gettext('Send email to contact person(s)') | translate"
    modal
    top="10vh"
    width="70vw"
    custom-class="SendEmailDialog"
    @opened="setSelectEvent"
  >
    <el-form @submit.native.prevent>
      <el-form-item :label="emailAddressString(rows)">
        <el-input
          ref="emailArea"
          v-model="selectable"
          :rows="rows < 10 ? rows : 10"
          readonly
          class="AddressesArea"
          type="textarea"
          @select="trackSelection"
        />
      </el-form-item>
    </el-form>
    <span slot="footer">
      <el-row type="flex" align="center">
        <el-col class="SecondaryButtons">
          <el-button type="text" class="IconLeft" @click="copy">
            <fa icon="clone" />
            <translate>Copy to clipboard</translate>
          </el-button>
        </el-col>
        <el-col class="PrimaryButtons">
          <el-button type="primary" @click="send">
            <translate>Send email(s)</translate>
          </el-button>
        </el-col>
      </el-row>
    </span>
  </el-dialog>
</template>

<script>
import { mapGetters } from 'vuex'
import uniqBy from 'lodash/uniqBy'
import { mapGettersActions } from '../../utilities/form.js'

export default {
  computed: {
    ...mapGetters({
      projects: 'dashboard/getProjectsBucket',
      profile: 'user/getProfile',
      selectAll: 'dashboard/getSelectAll',
      selectedRows: 'dashboard/getSelectedRows',
    }),
    ...mapGettersActions({
      visible: [
        'layout',
        'getSendEmailDialogState',
        'setSendEmailDialogState',
        0,
      ],
    }),
    addresses() {
      let projects = this.projects
      if (this.selectedRows && !this.selectAll) {
        projects = this.projects.filter((p) =>
          this.selectedRows.some((sr) => sr === p.id)
        )
      }
      return uniqBy(projects, 'contact_email')
    },
    rows() {
      return this.addresses ? this.addresses.length : 1
    },
    selectable() {
      return this.addresses
        ? this.addresses
            .map((a) => `${a.contact_name} <${a.contact_email}>`)
            .join('\n')
        : null
    },
  },
  methods: {
    emailAddressString(rows) {
      return this.$gettext('Email addresses ({rows})', { rows })
    },
    async copy() {
      await navigator.clipboard.writeText(this.selectable)
      this.trackCopyButton()
      this.$message({
        message: this.$gettext(
          'Email address(es) successfully copied in your clipboard'
        ),
        type: 'success',
      })
    },
    send() {
      const mailto = `mailto:${this.profile.email}?bcc=${this.addresses
        .map((a) => a.contact_email)
        .join(',')}`
      window.open(mailto)
    },
    setSelectEvent() {
      this.$refs.emailArea.$el.addEventListener('select', this.trackSelection)
    },
    trackSelection(event) {
      this.$matomo.trackEvent(
        'Select',
        'Select focal points',
        'Focal points selected'
      )
    },
    trackCopyButton() {
      this.$matomo.trackEvent(
        'Click',
        'Copy to clipboard',
        'Focal points copied to clipboard'
      )
    },
  },
}
</script>

<style></style>
