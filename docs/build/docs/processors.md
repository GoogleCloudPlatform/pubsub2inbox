# processors package

## Submodules

## processors.base module


### _exception_ processors.base.NoConfigKeySetException()
Bases: `Exception`


### _exception_ processors.base.NotConfiguredException()
Bases: `Exception`


### _class_ processors.base.Processor(config, jinja_environment, data, event, context)
Bases: [`BaseHelper`](helpers.md#helpers.base.BaseHelper)


#### expand_projects(projects)

#### _abstract static_ get_default_config_key()

#### _abstract_ process(output_var=None)

### _exception_ processors.base.ProcessorException()
Bases: `Exception`


### _exception_ processors.base.UnknownProjectException()
Bases: `Exception`

## processors.bigquery module


### _class_ processors.bigquery.BigqueryProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### get_default_config_key()

#### process(output_var='records')
## processors.budget module


### _class_ processors.budget.BudgetProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### get_default_config_key()

#### process(output_var={'budget': 'budget', 'projects': 'projects'})

### _exception_ processors.budget.MissingAttributesException()
Bases: `Exception`

## processors.cai module


### _class_ processors.cai.CaiProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### get_default_config_key()

#### process(output_var='assets')
## processors.clouddeploy module


### _class_ processors.clouddeploy.ClouddeployProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Operate Cloud Deploy applications, releases and other such things.


* **Parameters**

    
    * **project** (*str**, **optional*) – Google Cloud project ID.


    * **name** (*str*) – Name of the delivery pipeline.


    * **region** (*str*) – Google Cloud Deploy reiog.n


    * **mode** (*str*) – One of: releases.get, releases.create, releases.rollouts.create, releases.rollouts.get,
    releases.rollouts.approve, releases.rollouts.reject



#### get_default_config_key()

#### process(output_var='clouddeploy')

#### wait_for_operation_done(deploy_service, operation_name)
## processors.cloudrun module


### _class_ processors.cloudrun.CloudrunProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Fetches information and performs actions on Cloud Run (mainly Cloud Run Jobs).


* **Parameters**

    
    * **project** (*str**, **optional*) – Google Cloud project ID.


    * **location** (*str*) – Cloud Run location.


    * **job** (*str**, **optional*) – Cloud Run Job name.


    * **execution** (*str**, **optional*) – Cloud Run Job execution.


    * **task** (*str**, **optional*) – Cloud Run Job execution task.


    * **mode** (*str*) – One of: jobs.executions.list, jobs.executions.get, jobs.executions.cancel,
    jobs.run



#### get_default_config_key()

#### process(output_var='cloudrun')
## processors.compress module


### _class_ processors.compress.CompressProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Compress files to zip/tar/tgz formats.


* **Parameters**

    
    * **glob** (*str*) – Files to include, recursive. See Python glob().


    * **exclude** (*list**, **optional*) – List of files to exclude. See python fnmatch().


    * **output** (*str*) – Target file.


    * **format** (*str*) – One of: zip, tar, tar.gz, tar.bz2.


    * **compression** (*str**, **optional*) – Compression for ZIP: stored, bzip2, lzma. (default deflate)


    * **strip** (*int**, **optional*) – Remove N path parts in the archive.



#### get_default_config_key()

#### process(output_var='compress')
## processors.computeengine module


### _exception_ processors.computeengine.ComputeengineOperationFailed()
Bases: `Exception`


### _class_ processors.computeengine.ComputeengineProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Perform actions on Compute Engine instances.


* **Parameters**

    
    * **project** (*str**, **optional*) – Google Cloud project ID.


    * **instance** (*str*) – Instance to operate on.


    * **disk** (*str**, **optional*) – Disk to operate on.


    * **deviceName** (*str**, **optional*) – Device name to operate on.


    * **snapshotName** (*str**, **optional*) – Snapshot name (or regexp for disks.instanceSnapshots) for instant snapshots.


    * **maxSnapshots** (*int**, **optional*) – Maximum snapshots for disks.instanceSnapshots.purge.


    * **storageLocations** (*list**, **optional*) – Storage locations for disk.snapshots.


    * **snapshotParameters** (*dict**, **optional*) – Additional snapshot configuration.


    * **labels** (*dict**, **optional*) – Labels for instant snapshots.


    * **region** (*str**, **optional*) – Google Cloud region.


    * **zone** (*str**, **optional*) – Google Cloud zone for the instance.


    * **mode** (*str*) – One of: instances.get, instances.stop, instances.reset, instances.start,
    instances.detachDisk, instances.attachDisk, disks.instantSnapshots.create, disks.instantSnapshots.purge,
    disk.snapshots.create, disk.snapshots.purge



#### get_default_config_key()

#### get_instance(compute_service, project, zone, instance)

#### process(output_var='computeengine')

#### wait_for_operation_done(compute_service, operation_name, operation_self_link, project, zone, region, timeout=30)
## processors.containeranalysis module


### _class_ processors.containeranalysis.ContaineranalysisProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Fetch occurrences and notes from Container Analysis API.


* **Parameters**

    
    * **project** (*str**, **optional*) – Google Cloud project ID.


    * **name** (*str*) – Occurrence/note name (projects/…/occurrents/…).



#### get_default_config_key()

#### process(output_var='containeranalysis')
## processors.debug module


### _class_ processors.debug.DebugProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Dumps Jinja variable state to output. Useful for debugging.


#### get_default_config_key()

#### process(output_var='debug')
## processors.directory module


### _class_ processors.directory.DirectoryProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### get_default_config_key()

#### process(output_var='results')
## processors.dns module


### _class_ processors.dns.DnsProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Submit changes to Cloud DNS API. For more information, see:
[https://cloud.google.com/dns/docs/reference/v1/changes](https://cloud.google.com/dns/docs/reference/v1/changes)


* **Parameters**

    
    * **managedZone** (*str*) – Cloud DNS zone ID.


    * **project** (*str**, **optional*) – Google Cloud project ID.


    * **changes** (*dict*) – Changes to submit.



#### get_default_config_key()

#### process(output_var='dns')
## processors.docker module


### _class_ processors.docker.DockerProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Perform actions on Docker registries.


* **Parameters**

    
    * **hostname** (*str*) – Docker registry hostname.


    * **username** (*str**, **optional*) – Username for Docker registry. Defaults to SA authentication for Artifact Registry.


    * **password** (*str**, **optional*) – Password for Docker registry.


    * **image** (*str*) – Image to pull/push


    * **tag** (*str**, **optional*) – Tag to pull/push, defaults to latest.


    * **mode** (*str*) – image.copy, image.delete, image.deleteversion, images.list


    * **destination_hostname** (*str**, **optional*) – Docker registry hostname. (For copy)


    * **destination_username** (*str**, **optional*) – Username for Docker registry. Defaults to SA authentication for Artifact Registry. (For copy)


    * **destination_password** (*str**, **optional*) – Password for Docker registry. (For copy)


    * **destination_image** (*str*) – Image to pull/push


    * **destination_tag** (*str**, **optional*) – Tag to pull/push, defaults to latest.


    * **tls_verify** (*bool**, **optional*) – Set false to disable TLS verify at source registry.


    * **destination_tls_verify** (*bool**, **optional*) – Set false to disable TLS verify at destination registry.



#### destination_tls_verify(_ = Tru_ )

#### get_default_config_key()

#### process(output_var='docker')

#### source_tls_verify(_ = Tru_ )

#### wait_for_operation_done(ar_service, operation_name)
## processors.download module


### _class_ processors.download.DownloadProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Downloads files to “local filesystem”. Supports: HTTP, HTTPS, FTP, SFTP.


* **Parameters**

    
    * **url** (*str*) – URL to download.


    * **filename** (*str**, **optional*) – Filename to save.


    * **strip** (*int**, **optional*) – Strip N components from the save path.


    * **body** (*str**, **optional*) – Specify request body to issue a POST call.


    * **headers** (*dict**, **optional*) – Specify request headers.


    * **privateKey** (*dict**, **optional*) – Private key for SFTP (keys: key, type (rsa, ecdsa, ed25519), passphrase (optional))


    * **hostKey** (*dict**, **optional*) – Remote host public key, otherwise auto-accept (keys: hostname, keytype, key)



#### get_default_config_key()

#### process(output_var='download')
## processors.genericjson module


### _class_ processors.genericjson.GenericjsonProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### get_default_config_key()

#### process(output_var='data')
## processors.git module


### _class_ processors.git.GitProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Clones Git repositories via HTTPS or SSH.


* **Parameters**

    
    * **url** (*str*) – Repository URL to download.


    * **branch** (*str**, **optional*) – Branch to check out.


    * **directory** (*str**, **optional*) – Directory to clone into.


    * **depth** (*int**, **optional*) – Depth to check out.



#### get_default_config_key()

#### process(output_var='git')
## processors.github module


### _class_ processors.github.GithubProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Creates GitHub issues or comments.


* **Parameters**

    
    * **githubToken** (*str*) – A token for accessing GitHub (note: you can use the secret processor to retrieve it from Secrets Manager).


    * **baseUrl** (*str**, **optional*) – GitHub URL (defaults to [https://github.com](https://github.com))


    * **repository** (*str*) – GitHub repository to use.


    * **mode** (*str*) – One of: issues.list, issues.get, issues.create, comments.list, comments.get, comments.create.


    * **issueId** (*int**, **optional*) – Issue ID.


    * **commentId** (*int**, **optional*) – Comment ID.


    * **state** (*str**, **optional*) – Issue state.



#### get_default_config_key()

#### process(output_var='github')
## processors.groups module


### _class_ processors.groups.GroupsProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### get_default_config_key()

#### process(output_var={'all_groups': 'all_groups', 'groups_by_manager': 'groups_by_manager', 'groups_by_owner': 'groups_by_owner'})
## processors.loadbalancing module


### _exception_ processors.loadbalancing.LoadbalancingOperationFailed()
Bases: `Exception`


### _class_ processors.loadbalancing.LoadbalancingProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Perform actions on Cloud Load Balancers.


* **Parameters**

    
    * **project** (*str**, **optional*) – Google Cloud project ID.


    * **backend_service** (*str*) – Backend service to operate on.


    * **timeout** (*int**, **optional*) – Timeout of waiting on operations.


    * **region** (*str**, **optional*) – Google Cloud region.


    * **mode** (*str*) – One of: backendservice.get, regionbackendservice.get, backendservice.patch, regionbackendservice.patch



#### get_backend(compute_service, project, backend_service)

#### get_default_config_key()

#### get_region_backend(compute_service, project, region, backend_service)

#### process(output_var='loadbalancing')

#### wait_for_operation_done(compute_service, operation_name, operation_self_link, project, zone, region, timeout=30)
## processors.logging module


### _class_ processors.logging.LoggingProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Fetch logging information from Cloud Logging.


* **Parameters**

    
    * **project** (*str**, **optional*) – Google Cloud project ID.


    * **resourceNames** (*list*) – Parent resources to fetch logging entries from.


    * **filter** (*str**, **optional*) – Logging filter.


    * **orderBy** (*str**, **optional*) – How to order log entries.


    * **format** (*str**, **optional*) – One of: full, text-only, with-timestamps (default full)


    * **mode** (*str*) – One of: entries.list



#### get_default_config_key()

#### process(output_var='logging')
## processors.monitoring module


### _class_ processors.monitoring.MonitoringProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### get_default_config_key()

#### process(output_var='time_series')
## processors.opsgenie module


### _class_ processors.opsgenie.OpsgenieProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Create OpsGenie alerts and incidents.


* **Parameters**

    
    * **endpoint** (*str**, **optional*) – OpsGenie API endpoint (use [https://api.eu.opsgenie.com/v2](https://api.eu.opsgenie.com/v2) for EU).


    * **token** (*str*) – OpsGenie authentication token.


    * **mode** (*str*) – One of: alert.create, incident.create


    * **data** (*dict*) – Body data for API call.



#### get_default_config_key()

#### process(output_var='opsgenie')
## processors.projects module


### _class_ processors.projects.ProjectsProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


#### get_default_config_key()

#### process(output_var='projects')
## processors.recommendations module


### _class_ processors.recommendations.RecommendationsProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


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


#### get_default_config_key()

#### process(output_var={'finding': 'finding', 'organization': 'organization', 'projects': 'projects'})
## processors.secret module


### _class_ processors.secret.SecretProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Fetch secrets from Secret Manager API and store them in Jinja
environment.


* **Parameters**

    
    * **project** (*str**, **optional*) – Google Cloud project ID.


    * **secret** (*str*) – Secret name.


    * **version** (*str**, **optional*) – Secret version, defaults to “latest”.


    * **mode** (*str**, **optional*) – Mode of operation, by default leaves data untouched.
    Also supports “json” to parse JSON, “yaml” for YAML, “base64” for base64.



#### get_default_config_key()

#### process(output_var='secret')
## processors.setvariable module


### _class_ processors.setvariable.SetvariableProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Outputs the contents of value. Control the execution via runIf and
the variable set with output.


* **Parameters**

    
    * **value** (*any*) – Value to set.


    * **fromJson** (*bool**, **optional*) – Convert value from JSON.



#### get_default_config_key()

#### process(output_var='variable')
## processors.shellscript module


### _exception_ processors.shellscript.CommandFailedException()
Bases: `Exception`


### _class_ processors.shellscript.ShellscriptProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Runs any shellscript as a command and exposes the output in Jinja.


* **Parameters**

    
    * **command** (*str*) – Command to execute.


    * **args** (*list**, **optional*) – List of arguments.


    * **enviroment** (*dict**, **optional*) – Additional environment variables to set.


    * **stdin** (*str**, **optional*) – Contents to pass via stdin to the process.


    * **json** (*bool**, **optional*) – Interpret the output as JSON.


    * **jsonMultiline** (*bool**, **optional*) – Interpret the output as multiline JSON.


    * **yaml** (*bool**, **optional*) – Interpret the output as YAML.


    * **csv** (*bool**, **optional*) – Interpret the output as CSV.


    * **tsv** (*bool**, **optional*) – Interpret the output as TSV.


    * **exitcodes** (*list**, **optional*) – List of allowed exit codes that are interpreted as successful run.



#### get_default_config_key()

#### process(output_var='shellscript')
## processors.slack module


### _class_ processors.slack.SlackProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Slack processor for fetching messages.


* **Parameters**

    
    * **token** (*str*) – A Slack Bot User OAuth Token.


    * **api** (*str*) – One of: conversations.list, conversations.history, conversations.replies


    * **(****str** (*mode*) – api, processMessages or lastImage (default api)


    * **optional** – api, processMessages or lastImage (default api)


    * **multimodal** (*bool**, **optional*) – Use multi-modal processing in processMessages.


    * **messages** (*list**, **optional*) – List of messages to process.


    * **appId** (*str**, **optional*) – The app ID to detect bot messages.


    * **prompt** (*str**, **optional*) – Initial message to append to the beginning of the conversation.


    * **request** (*dict*) – The API call body.



#### call_slack(api, token, request, urlencoded=False)

#### download_slack(url, token)

#### get_default_config_key()

#### process(output_var='slack')
## processors.storage module


### _class_ processors.storage.StorageProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`


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



#### get_default_config_key()

#### process(output_var='transcode')
## processors.vertexai module


### _class_ processors.vertexai.VertexaiProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Vertex AI processor.


* **Parameters**

    
    * **region** (*str*) – Endpoint to use.


    * **mode** (*str*) – search (Vertex AI Search)


    * **method** (*str**, **optional*) – Method to call (defaults to “search”).


    * **project** (*str**, **optional*) – Google Cloud project ID.


    * **location** (*str*) – Location for Vertex AI.


    * **collection** (*str**, **optional*) – Collection (defaults to “default_collection”)


    * **engineId** (*str*) – Engine ID.


    * **datastoreId** (*str*) – Data store ID (either this or engineId).


    * **servingConfig** (*str**, **optional*) – Serving configuration (defaults to “default_config”).


    * **returnErrors** (*bool**, **optional*) – Set to true to return errors


    * **apiVersion** (*str**, **optional*) – API version, defaults to “v1”.


    * **request** (*dict*) – Request.



#### get_default_config_key()

#### process(output_var='vertexai')
## processors.vertexgenai module


### _class_ processors.vertexgenai.VertexgenaiProcessor(config, jinja_environment, data, event, context)
Bases: `Processor`

Vertex AI Generative AI processor.


* **Parameters**

    
    * **region** (*str*) – Endpoint to use.


    * **modelId** (*str*) – Deployed model to use.


    * **project** (*str**, **optional*) – Google Cloud project ID.


    * **method** (*str**, **optional*) – Method to call, by default: “predict”


    * **returnErrors** (*bool**, **optional*) – Set to true to return errors


    * **callFunctions** (*dict**, **optional*) – URLs for functions.


    * **request** (*dict*) – Request.



#### call_function(name, params)

#### get_default_config_key()

#### process(output_var='vertexgenai')
## Module contents
