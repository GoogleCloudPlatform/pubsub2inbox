# processors package

## Submodules

## processors.base module


### _exception_ processors.base.NotConfiguredException()
Bases: `Exception`


### _class_ processors.base.Processor(config, jinja_environment, data, event, context)
Bases: [`BaseHelper`](helpers.md#helpers.base.BaseHelper)


#### config(_ = Non_ )

#### context(_: Contex_ )

#### data(_ = Non_ )

#### event(_ = Non_ )

#### expand_projects(projects)

#### _abstract_ process(config_key=None)

### _exception_ processors.base.UnknownProjectException()
Bases: `Exception`

## processors.bigquery module


### _class_ processors.bigquery.BigqueryProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### process(config_key=None)
## processors.budget module


### _class_ processors.budget.BudgetProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### process(config_key=None)

### _exception_ processors.budget.MissingAttributesException()
Bases: `Exception`

## processors.cai module


### _class_ processors.cai.CaiProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### process(config_key=None)
## processors.directory module


### _class_ processors.directory.DirectoryProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### process(config_key=None)
## processors.genericjson module


### _class_ processors.genericjson.GenericjsonProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### process(config_key=None)
## processors.groups module


### _class_ processors.groups.GroupsProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### process(config_key=None)
## processors.monitoring module


### _class_ processors.monitoring.MonitoringProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### process(config_key=None)
## processors.projects module


### _class_ processors.projects.ProjectsProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### process(config_key=None)
## processors.recommendations module


### _class_ processors.recommendations.RecommendationsProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_insights(client, insight_types, parents, all_locations, filter)
Fetches insights with specified insight types from applicable locations


#### get_link(parent)

#### get_recommendations(client, recommender_types, parents, all_locations, filter)
Fetches recommendations with specified recommender types from applicable locations


#### get_regions(compute_service, project_id, location_filters)
Fetches all regions for a project


#### get_zones(compute_service, project_id, location_filters)
Fetches all zones for a project


#### insights(_ = {_ )

#### is_billing_account(parent)

#### is_folder(parent)

#### is_global(region)

#### is_multi_region(region)

#### is_organization(parent)

#### is_project(parent)

#### is_region(region)

#### is_zone(zone)

#### multi_regions(_ = ['global', 'us', 'europe', 'asia'_ )

#### process(config_key=None)

#### recommenders(_ = {_ )

#### rollup_insights(insights)

#### rollup_recommendations(recommendations)

### _exception_ processors.recommendations.UnknownRecommenderException()
Bases: `Exception`

## processors.scc module


### _class_ processors.scc.SccProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### process(config_key=None)
## processors.shellscript module


### _exception_ processors.shellscript.CommandFailedException()
Bases: `Exception`


### _class_ processors.shellscript.ShellscriptProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### process(config_key=None)
## processors.storage module


### _class_ processors.storage.StorageProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### process(config_key=None)
## Module contents
