export const nameInventMapping = {
  // INVENT
  functions: 'Function(s) of Platform',
  hardware: 'Hardware platforms',
  nontech: 'Non-Technology platforms',
  regional_priorities: 'Regional Priorities',
  innovation_categories: 'Innovation Categories',
  cpd: 'In Country programme document (CPD)',
  // phases: 'Phase of Initiative'
}

export const apiNameInvenMapping = {
  functions: 'getFunctions',
  hardware: 'getHardware',
  nontech: 'getNontech',
  regional_priorities: 'getRegionalPriorities',
  innovation_categories: 'getInnovationCategories',
  cpd: 'getCpd',
}

export const nameMapping = {
  name: 'Project Name',
  implementation_overview: 'Initiative Description',
  start_date: 'Project Start Date',
  end_date: 'Project End Date',
  contact_name: 'Programme Focal Point Name',
  contact_email: 'Programme Focal Point Email',
  platforms: 'Software',
  health_focus_areas: 'Health Focus Areas',
  hsc_challenges: 'Health System Challenges',
  dhis: 'Digital Health Interventions',
  goal_area: 'Goal Area',
  result_area: 'Result Area',
  capability_levels: 'Capability Levels',
  capability_categories: 'Capability Categories',
  capability_subcategories: 'Capability Subcategories',
  field_office: 'Field Office',
  ...nameInventMapping,
}

export const importTemplate = [
  {
    'Project Name': 'MyProject',
    'Initiative Description': 'Narrative free text',
    'Project Start Date': '01/01/2015',
    'Project End Date': '01/01/2019',
    'Programme Focal Point Name': 'Nico',
    'Programme Focal Point Email': 'nico@pulilab.com',
    Software: 'Bamboo',
    'Digital Health Interventions':
      '3.4.1 Notify birth event|3.4.2 Register birth event',
    'Health Focus Areas':
      'Adolescents and communicable diseases|Other sexual and reproductive health',
    'Health System Challenges':
      '1.1 Lack of population denominator|1.2 Delayed reporting of events',
    'Goal Area': '21. Survive and Thrive',
    'Result Area': '21-01 Maternal and newborn health',
    'Field Office': 'According to selected country office',
  },
  {
    'Project Name': 'MyProject2',
    'Initiative Description': 'Narrative free text',
    'Project Start Date': '04/22/2015',
    'Project End Date': '03/22/2019',
    'Programme Focal Point Name': 'Nico',
    'Programme Focal Point Email': 'nico@pulilab.com',
    Software: 'Bamboo',
    'Goal Area': '22. Learn',
    'Result Area': '22-01 Equitable access to quality education',
    'Field Office': 'According to selected country office',
    'Capability Levels': '4. Interventions for data services',
    'Capability Categories': '1.3 Student to student communication',
    'Capability Subcategories':
      '1.1.1 Transmit education event alerts to specific population group(s)',
  },
]
