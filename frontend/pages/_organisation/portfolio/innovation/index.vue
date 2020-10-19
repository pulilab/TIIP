<template>
  <section class="portfolio-main">
    <h1>
      <translate>What is UNICEF’s Approach of Portfolio Management</translate>
    </h1>
    <h2>
      <translate>Explore Our Portfolio-Driven Portfolios</translate>
    </h2>
    <p>
      <translate>
        Our priority portfolios for innovation are driven by the key problems we
        seek to solve for children. Please select a problem statement from one
        of the portfolios below to learn more.
      </translate>
    </p>
    <p>
      <translate>
        Dynamically populated based on the portfolio data set.
      </translate>
    </p>

    <el-collapse v-model="activePortfolio" accordion class="MainAccordion">
      <el-collapse-item
        v-for="portfolio in portfolios"
        :key="portfolio.name"
        :name="portfolio.id"
      >
        <div slot="title" class="AccordionTitle">
          <span class="accordion-status"></span>
          <span :class="`icon-circle icon-tiip-${portfolio.icon}`">&nbsp;</span>
          <span class="portfolio-title">{{ portfolio.name }}</span>
          <nuxt-link
            :to="
              localePath({
                name: 'organisation-portfolio-innovation-id',
                params: { organisation: '-', id: portfolio.id },
              })
            "
          >
            <translate>View Portfolio</translate>
          </nuxt-link>
        </div>
        <div class="AccordionContent">
          <el-row>
            <el-col :span="12" class="col-container">
              <div class="col-title">
                <translate>Problem Statements</translate>
              </div>
              <el-collapse v-model="activePS" accordion class="SubAccordion">
                <el-collapse-item
                  v-for="{ name, id, description } in portfolio.ps"
                  :key="name"
                  :name="id"
                >
                  <div slot="title" class="SubAccordionTitle">
                    {{ name }}
                  </div>
                  <div class="SubAccordionContent">
                    {{ description }}
                  </div>
                </el-collapse-item>
              </el-collapse>
            </el-col>
            <el-col :span="12" class="col-container">
              <div class="col-title">
                <translate>Summary</translate>
              </div>
              <p class="summary">
                {{ portfolio.description }}
              </p>
              <template v-if="false">
                <div class="col-title">
                  <translate>Contact person</translate>
                </div>
                <div class="contact">
                  Edson Monteiro <br />
                  <a href="mailto:emonterio@unicef.org">emonterio@unicef.org</a>
                </div>
              </template>
            </el-col>
          </el-row>
        </div>
      </el-collapse-item>
    </el-collapse>
    <info-card class="InfoCard" />
  </section>
</template>

<script>
export default {}
</script>

<style lang="less" scoped></style>
