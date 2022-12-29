# processors package

## Submodules

## processors.base module


### _exception_ processors.base.NoConfigKeySetException()
Bases: `Exception`


### _exception_ processors.base.NotConfiguredException()
Bases: `Exception`


### _class_ processors.base.Processor(config, jinja_environment, data, event, context)
Bases: [`BaseHelper`](helpers.md#helpers.base.BaseHelper)


#### config(_ = Non_ )

#### context(_: Contex_ )

#### data(_ = Non_ )

#### event(_ = Non_ )

#### expand_projects(projects)

#### _abstract static_ get_default_config_key()

#### _abstract_ process(output_var=None)

### _exception_ processors.base.UnknownProjectException()
Bases: `Exception`

## processors.bigquery module


### _class_ processors.bigquery.BigqueryProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_default_config_key()

#### process(output_var='records')
## processors.budget module


### _class_ processors.budget.BudgetProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_default_config_key()

#### process(output_var={'budget': 'budget', 'projects': 'projects'})

### _exception_ processors.budget.MissingAttributesException()
Bases: `Exception`

## processors.cai module


### _class_ processors.cai.CaiProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_default_config_key()

#### process(output_var='assets')
## processors.directory module


### _class_ processors.directory.DirectoryProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_default_config_key()

#### process(output_var='results')
## processors.genericjson module


### _class_ processors.genericjson.GenericjsonProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_default_config_key()

#### process(output_var='data')
## processors.groups module


### _class_ processors.groups.GroupsProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_default_config_key()

#### process(output_var={'all_groups': 'all_groups', 'groups_by_manager': 'groups_by_manager', 'groups_by_owner': 'groups_by_owner'})
## processors.monitoring module


### _class_ processors.monitoring.MonitoringProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_default_config_key()

#### process(output_var='time_series')
## processors.projects module


### _class_ processors.projects.ProjectsProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_default_config_key()

#### process(output_var='projects')
## processors.recommendations module


### _class_ processors.recommendations.RecommendationsProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_default_config_key()

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

#### process(output_var={'insights': 'insights', 'insights_rollup': 'insights_rollup', 'recommendations': 'recommendations', 'recommendations_rollup': 'recommendations_rollup'})

#### recommenders(_ = {_ )

#### rollup_insights(insights)

#### rollup_recommendations(recommendations)

### _exception_ processors.recommendations.UnknownRecommenderException()
Bases: `Exception`

## processors.scc module


### _class_ processors.scc.SccProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_default_config_key()

#### process(output_var={'finding': 'finding', 'organization': 'organization', 'projects': 'projects'})
## processors.shellscript module


### _exception_ processors.shellscript.CommandFailedException()
Bases: `Exception`


### _class_ processors.shellscript.ShellscriptProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_default_config_key()

#### process(output_var='shellscript')
## processors.storage module


### _class_ processors.storage.StorageProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### context(_: Contex_ )

#### get_default_config_key()

#### process(output_var='object')
## processors.transcode module


### _exception_ processors.transcode.InvalidModeException()
Bases: `Exception`


### _class_ processors.transcode.TranscodeProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Transcode media using Transcoder API. For more information, see:
[https://cloud.google.com/transcoder/docs](https://cloud.google.com/transcoder/docs)


* **Parameters**

    
    * **mode** (*enum**, **optional*) – Select mode: create (creates a new job), get (gets existing job)


    * **project** (*str**, **optional*) – Google Cloud project ID.


    * **location** (*str*) – Processing location (eg. “europe-west4”)


    * **job** (*dict*) – Transcoding job configuration.



#### context(_: Contex_ )

#### get_default_config_key()

#### process(output_var='transcode')
## Module contents
