# pubsub2inbox


* [filters package](filters.md)


    * [Submodules](filters.md#submodules)


    * [filters.date module](filters.md#module-filters.date)


        * [`InvalidDatetimeException`](filters.md#filters.date.InvalidDatetimeException)


        * [`InvalidRecurringDateException`](filters.md#filters.date.InvalidRecurringDateException)


        * [`recurring_date()`](filters.md#filters.date.recurring_date)


        * [`strftime()`](filters.md#filters.date.strftime)


        * [`utc_strftime()`](filters.md#filters.date.utc_strftime)


    * [filters.gcp module](filters.md#module-filters.gcp)


        * [`format_cost()`](filters.md#filters.gcp.format_cost)


        * [`get_cost()`](filters.md#filters.gcp.get_cost)


        * [`get_gcp_resource()`](filters.md#filters.gcp.get_gcp_resource)


    * [filters.lists module](filters.md#module-filters.lists)


        * [`index()`](filters.md#filters.lists.index)


        * [`merge_dict()`](filters.md#filters.lists.merge_dict)


        * [`split()`](filters.md#filters.lists.split)


    * [filters.regex module](filters.md#module-filters.regex)


        * [`regex_match()`](filters.md#filters.regex.regex_match)


        * [`regex_replace()`](filters.md#filters.regex.regex_replace)


        * [`regex_search()`](filters.md#filters.regex.regex_search)


    * [filters.strings module](filters.md#module-filters.strings)


        * [`InvalidSchemeSignedURLException`](filters.md#filters.strings.InvalidSchemeSignedURLException)


        * [`InvalidSchemeURLException`](filters.md#filters.strings.InvalidSchemeURLException)


        * [`ObjectNotFoundException`](filters.md#filters.strings.ObjectNotFoundException)


        * [`add_links()`](filters.md#filters.strings.add_links)


        * [`b64decode()`](filters.md#filters.strings.b64decode)


        * [`csv_encode()`](filters.md#filters.strings.csv_encode)


        * [`filemagic()`](filters.md#filters.strings.filemagic)


        * [`generate_signed_url()`](filters.md#filters.strings.generate_signed_url)


        * [`hash_string()`](filters.md#filters.strings.hash_string)


        * [`html_table_to_xlsx()`](filters.md#filters.strings.html_table_to_xlsx)


        * [`json_decode()`](filters.md#filters.strings.json_decode)


        * [`json_encode()`](filters.md#filters.strings.json_encode)


        * [`ltrim()`](filters.md#filters.strings.ltrim)


        * [`make_list()`](filters.md#filters.strings.make_list)


        * [`parse_string()`](filters.md#filters.strings.parse_string)


        * [`parse_url()`](filters.md#filters.strings.parse_url)


        * [`re_escape()`](filters.md#filters.strings.re_escape)


        * [`read_file()`](filters.md#filters.strings.read_file)


        * [`read_file_b64()`](filters.md#filters.strings.read_file_b64)


        * [`read_gcs_object()`](filters.md#filters.strings.read_gcs_object)


        * [`remove_mrkdwn()`](filters.md#filters.strings.remove_mrkdwn)


        * [`rtrim()`](filters.md#filters.strings.rtrim)


        * [`trim()`](filters.md#filters.strings.trim)


        * [`urlencode()`](filters.md#filters.strings.urlencode)


        * [`yaml_decode()`](filters.md#filters.strings.yaml_decode)


        * [`yaml_encode()`](filters.md#filters.strings.yaml_encode)


    * [filters.tests module](filters.md#module-filters.tests)


        * [`test_contains()`](filters.md#filters.tests.test_contains)


    * [Module contents](filters.md#module-filters)


        * [`get_jinja_filters()`](filters.md#filters.get_jinja_filters)


        * [`get_jinja_tests()`](filters.md#filters.get_jinja_tests)


* [helpers package](helpers.md)


    * [Submodules](helpers.md#submodules)


    * [helpers.base module](helpers.md#module-helpers.base)


        * [`BaseHelper`](helpers.md#helpers.base.BaseHelper)


            * [`BaseHelper.get_project_number()`](helpers.md#helpers.base.BaseHelper.get_project_number)


            * [`BaseHelper.get_token_for_scopes()`](helpers.md#helpers.base.BaseHelper.get_token_for_scopes)


            * [`BaseHelper.logger`](helpers.md#helpers.base.BaseHelper.logger)


        * [`Context`](helpers.md#helpers.base.Context)


        * [`NoCredentialsException`](helpers.md#helpers.base.NoCredentialsException)


        * [`get_branded_http()`](helpers.md#helpers.base.get_branded_http)


        * [`get_grpc_client_info()`](helpers.md#helpers.base.get_grpc_client_info)


        * [`get_user_agent()`](helpers.md#helpers.base.get_user_agent)


    * [Module contents](helpers.md#module-helpers)


* [main module](main.md)


    * [`CloudRunServer`](main.md#main.CloudRunServer)


        * [`CloudRunServer.on_get()`](main.md#main.CloudRunServer.on_get)


        * [`CloudRunServer.on_post()`](main.md#main.CloudRunServer.on_post)


    * [`ConcurrencyRetryException`](main.md#main.ConcurrencyRetryException)


    * [`InvalidMessageFormatException`](main.md#main.InvalidMessageFormatException)


    * [`MalformedGlobalsException`](main.md#main.MalformedGlobalsException)


    * [`MalformedMacrosException`](main.md#main.MalformedMacrosException)


    * [`MalformedTypeInPipelineException`](main.md#main.MalformedTypeInPipelineException)


    * [`MessageTooOldException`](main.md#main.MessageTooOldException)


    * [`NoDataFieldException`](main.md#main.NoDataFieldException)


    * [`NoMessageReceivedException`](main.md#main.NoMessageReceivedException)


    * [`NoOutputsConfiguredException`](main.md#main.NoOutputsConfiguredException)


    * [`NoPipelineConfiguredException`](main.md#main.NoPipelineConfiguredException)


    * [`NoResendConfigException`](main.md#main.NoResendConfigException)


    * [`NoTypeConfiguredException`](main.md#main.NoTypeConfiguredException)


    * [`NoTypeInPipelineException`](main.md#main.NoTypeInPipelineException)


    * [`check_retry_period()`](main.md#main.check_retry_period)


    * [`decode_and_process()`](main.md#main.decode_and_process)


    * [`get_concurrency_params()`](main.md#main.get_concurrency_params)


    * [`get_jinja_environment()`](main.md#main.get_jinja_environment)


    * [`get_jinja_escaping()`](main.md#main.get_jinja_escaping)


    * [`handle_concurrency_post()`](main.md#main.handle_concurrency_post)


    * [`handle_concurrency_pre()`](main.md#main.handle_concurrency_pre)


    * [`handle_ignore_on()`](main.md#main.handle_ignore_on)


    * [`load_configuration()`](main.md#main.load_configuration)


    * [`macro_helper()`](main.md#main.macro_helper)


    * [`process_message()`](main.md#main.process_message)


    * [`process_message_legacy()`](main.md#main.process_message_legacy)


    * [`process_message_pipeline()`](main.md#main.process_message_pipeline)


    * [`process_pubsub()`](main.md#main.process_pubsub)


    * [`process_pubsub_v2()`](main.md#main.process_pubsub_v2)


    * [`run_webserver()`](main.md#main.run_webserver)


    * [`setup_logging()`](main.md#main.setup_logging)


* [output package](output.md)


    * [Submodules](output.md#submodules)


    * [output.base module](output.md#module-output.base)


        * [`NotConfiguredException`](output.md#output.base.NotConfiguredException)


        * [`Output`](output.md#output.base.Output)


            * [`Output.output()`](output.md#output.base.Output.output)


    * [output.bigquery module](output.md#module-output.bigquery)


        * [`BigqueryOutput`](output.md#output.bigquery.BigqueryOutput)


            * [`BigqueryOutput.output()`](output.md#output.bigquery.BigqueryOutput.output)


        * [`InvalidJobOptionException`](output.md#output.bigquery.InvalidJobOptionException)


    * [output.chat module](output.md#module-output.chat)


        * [`ChatOutput`](output.md#output.chat.ChatOutput)


            * [`ChatOutput.output()`](output.md#output.chat.ChatOutput.output)


    * [output.delay module](output.md#module-output.delay)


        * [`DelayOutput`](output.md#output.delay.DelayOutput)


            * [`DelayOutput.output()`](output.md#output.delay.DelayOutput.output)


    * [output.gcs module](output.md#module-output.gcs)


        * [`GcsOutput`](output.md#output.gcs.GcsOutput)


            * [`GcsOutput.output()`](output.md#output.gcs.GcsOutput.output)


    * [output.gcscopy module](output.md#module-output.gcscopy)


        * [`GcscopyOutput`](output.md#output.gcscopy.GcscopyOutput)


            * [`GcscopyOutput.output()`](output.md#output.gcscopy.GcscopyOutput.output)


    * [output.groupssettings module](output.md#module-output.groupssettings)


        * [`GroupssettingsOutput`](output.md#output.groupssettings.GroupssettingsOutput)


            * [`GroupssettingsOutput.output()`](output.md#output.groupssettings.GroupssettingsOutput.output)


    * [output.logger module](output.md#module-output.logger)


        * [`LoggerOutput`](output.md#output.logger.LoggerOutput)


            * [`LoggerOutput.output()`](output.md#output.logger.LoggerOutput.output)


    * [output.mail module](output.md#module-output.mail)


        * [`AllTransportsFailedException`](output.md#output.mail.AllTransportsFailedException)


        * [`DownloadFailedException`](output.md#output.mail.DownloadFailedException)


        * [`GroupNotFoundException`](output.md#output.mail.GroupNotFoundException)


        * [`InvalidSchemeException`](output.md#output.mail.InvalidSchemeException)


        * [`MailOutput`](output.md#output.mail.MailOutput)


            * [`MailOutput.embed_images()`](output.md#output.mail.MailOutput.embed_images)


            * [`MailOutput.expand_recipients()`](output.md#output.mail.MailOutput.expand_recipients)


            * [`MailOutput.output()`](output.md#output.mail.MailOutput.output)


            * [`MailOutput.send_via_msgraphapi()`](output.md#output.mail.MailOutput.send_via_msgraphapi)


            * [`MailOutput.send_via_sendgrid()`](output.md#output.mail.MailOutput.send_via_sendgrid)


            * [`MailOutput.send_via_smtp()`](output.md#output.mail.MailOutput.send_via_smtp)


        * [`MultipleSendersException`](output.md#output.mail.MultipleSendersException)


        * [`OAuthTokenFetchException`](output.md#output.mail.OAuthTokenFetchException)


    * [output.pubsub module](output.md#module-output.pubsub)


        * [`PubsubOutput`](output.md#output.pubsub.PubsubOutput)


            * [`PubsubOutput.callback()`](output.md#output.pubsub.PubsubOutput.callback)


            * [`PubsubOutput.output()`](output.md#output.pubsub.PubsubOutput.output)


    * [output.scc module](output.md#module-output.scc)


        * [`SccOutput`](output.md#output.scc.SccOutput)


            * [`SccOutput.output()`](output.md#output.scc.SccOutput.output)


    * [output.slack module](output.md#module-output.slack)


        * [`SlackOutput`](output.md#output.slack.SlackOutput)


            * [`SlackOutput.output()`](output.md#output.slack.SlackOutput.output)


    * [output.test module](output.md#module-output.test)


        * [`TestFailedException`](output.md#output.test.TestFailedException)


        * [`TestOutput`](output.md#output.test.TestOutput)


            * [`TestOutput.output()`](output.md#output.test.TestOutput.output)


    * [output.twilio module](output.md#module-output.twilio)


        * [`TwilioOutput`](output.md#output.twilio.TwilioOutput)


            * [`TwilioOutput.output()`](output.md#output.twilio.TwilioOutput.output)


    * [output.webhook module](output.md#module-output.webhook)


        * [`WebhookOutput`](output.md#output.webhook.WebhookOutput)


            * [`WebhookOutput.output()`](output.md#output.webhook.WebhookOutput.output)


    * [Module contents](output.md#module-output)


* [processors package](processors.md)


    * [Submodules](processors.md#submodules)


    * [processors.base module](processors.md#module-processors.base)


        * [`NoConfigKeySetException`](processors.md#processors.base.NoConfigKeySetException)


        * [`NotConfiguredException`](processors.md#processors.base.NotConfiguredException)


        * [`Processor`](processors.md#processors.base.Processor)


            * [`Processor.expand_projects()`](processors.md#processors.base.Processor.expand_projects)


            * [`Processor.get_default_config_key()`](processors.md#processors.base.Processor.get_default_config_key)


            * [`Processor.process()`](processors.md#processors.base.Processor.process)


        * [`ProcessorException`](processors.md#processors.base.ProcessorException)


        * [`UnknownProjectException`](processors.md#processors.base.UnknownProjectException)


    * [processors.bigquery module](processors.md#module-processors.bigquery)


        * [`BigqueryProcessor`](processors.md#processors.bigquery.BigqueryProcessor)


            * [`BigqueryProcessor.get_default_config_key()`](processors.md#processors.bigquery.BigqueryProcessor.get_default_config_key)


            * [`BigqueryProcessor.process()`](processors.md#processors.bigquery.BigqueryProcessor.process)


    * [processors.budget module](processors.md#module-processors.budget)


        * [`BudgetProcessor`](processors.md#processors.budget.BudgetProcessor)


            * [`BudgetProcessor.get_default_config_key()`](processors.md#processors.budget.BudgetProcessor.get_default_config_key)


            * [`BudgetProcessor.process()`](processors.md#processors.budget.BudgetProcessor.process)


        * [`MissingAttributesException`](processors.md#processors.budget.MissingAttributesException)


    * [processors.cai module](processors.md#module-processors.cai)


        * [`CaiProcessor`](processors.md#processors.cai.CaiProcessor)


            * [`CaiProcessor.get_default_config_key()`](processors.md#processors.cai.CaiProcessor.get_default_config_key)


            * [`CaiProcessor.process()`](processors.md#processors.cai.CaiProcessor.process)


    * [processors.clouddeploy module](processors.md#module-processors.clouddeploy)


        * [`ClouddeployProcessor`](processors.md#processors.clouddeploy.ClouddeployProcessor)


            * [`ClouddeployProcessor.get_default_config_key()`](processors.md#processors.clouddeploy.ClouddeployProcessor.get_default_config_key)


            * [`ClouddeployProcessor.process()`](processors.md#processors.clouddeploy.ClouddeployProcessor.process)


            * [`ClouddeployProcessor.wait_for_operation_done()`](processors.md#processors.clouddeploy.ClouddeployProcessor.wait_for_operation_done)


    * [processors.cloudrun module](processors.md#module-processors.cloudrun)


        * [`CloudrunProcessor`](processors.md#processors.cloudrun.CloudrunProcessor)


            * [`CloudrunProcessor.get_default_config_key()`](processors.md#processors.cloudrun.CloudrunProcessor.get_default_config_key)


            * [`CloudrunProcessor.process()`](processors.md#processors.cloudrun.CloudrunProcessor.process)


    * [processors.compress module](processors.md#module-processors.compress)


        * [`CompressProcessor`](processors.md#processors.compress.CompressProcessor)


            * [`CompressProcessor.get_default_config_key()`](processors.md#processors.compress.CompressProcessor.get_default_config_key)


            * [`CompressProcessor.process()`](processors.md#processors.compress.CompressProcessor.process)


    * [processors.computeengine module](processors.md#module-processors.computeengine)


        * [`ComputeengineOperationFailed`](processors.md#processors.computeengine.ComputeengineOperationFailed)


        * [`ComputeengineProcessor`](processors.md#processors.computeengine.ComputeengineProcessor)


            * [`ComputeengineProcessor.get_default_config_key()`](processors.md#processors.computeengine.ComputeengineProcessor.get_default_config_key)


            * [`ComputeengineProcessor.get_instance()`](processors.md#processors.computeengine.ComputeengineProcessor.get_instance)


            * [`ComputeengineProcessor.process()`](processors.md#processors.computeengine.ComputeengineProcessor.process)


            * [`ComputeengineProcessor.wait_for_operation_done()`](processors.md#processors.computeengine.ComputeengineProcessor.wait_for_operation_done)


    * [processors.containeranalysis module](processors.md#module-processors.containeranalysis)


        * [`ContaineranalysisProcessor`](processors.md#processors.containeranalysis.ContaineranalysisProcessor)


            * [`ContaineranalysisProcessor.get_default_config_key()`](processors.md#processors.containeranalysis.ContaineranalysisProcessor.get_default_config_key)


            * [`ContaineranalysisProcessor.process()`](processors.md#processors.containeranalysis.ContaineranalysisProcessor.process)


    * [processors.debug module](processors.md#module-processors.debug)


        * [`DebugProcessor`](processors.md#processors.debug.DebugProcessor)


            * [`DebugProcessor.get_default_config_key()`](processors.md#processors.debug.DebugProcessor.get_default_config_key)


            * [`DebugProcessor.process()`](processors.md#processors.debug.DebugProcessor.process)


    * [processors.directory module](processors.md#module-processors.directory)


        * [`DirectoryProcessor`](processors.md#processors.directory.DirectoryProcessor)


            * [`DirectoryProcessor.get_default_config_key()`](processors.md#processors.directory.DirectoryProcessor.get_default_config_key)


            * [`DirectoryProcessor.process()`](processors.md#processors.directory.DirectoryProcessor.process)


    * [processors.dns module](processors.md#module-processors.dns)


        * [`DnsProcessor`](processors.md#processors.dns.DnsProcessor)


            * [`DnsProcessor.get_default_config_key()`](processors.md#processors.dns.DnsProcessor.get_default_config_key)


            * [`DnsProcessor.process()`](processors.md#processors.dns.DnsProcessor.process)


    * [processors.download module](processors.md#module-processors.download)


        * [`DownloadProcessor`](processors.md#processors.download.DownloadProcessor)


            * [`DownloadProcessor.get_default_config_key()`](processors.md#processors.download.DownloadProcessor.get_default_config_key)


            * [`DownloadProcessor.process()`](processors.md#processors.download.DownloadProcessor.process)


    * [processors.genericjson module](processors.md#module-processors.genericjson)


        * [`GenericjsonProcessor`](processors.md#processors.genericjson.GenericjsonProcessor)


            * [`GenericjsonProcessor.get_default_config_key()`](processors.md#processors.genericjson.GenericjsonProcessor.get_default_config_key)


            * [`GenericjsonProcessor.process()`](processors.md#processors.genericjson.GenericjsonProcessor.process)


    * [processors.git module](processors.md#module-processors.git)


        * [`GitProcessor`](processors.md#processors.git.GitProcessor)


            * [`GitProcessor.get_default_config_key()`](processors.md#processors.git.GitProcessor.get_default_config_key)


            * [`GitProcessor.process()`](processors.md#processors.git.GitProcessor.process)


    * [processors.github module](processors.md#module-processors.github)


        * [`GithubProcessor`](processors.md#processors.github.GithubProcessor)


            * [`GithubProcessor.get_default_config_key()`](processors.md#processors.github.GithubProcessor.get_default_config_key)


            * [`GithubProcessor.process()`](processors.md#processors.github.GithubProcessor.process)


    * [processors.groups module](processors.md#module-processors.groups)


        * [`GroupsProcessor`](processors.md#processors.groups.GroupsProcessor)


            * [`GroupsProcessor.get_default_config_key()`](processors.md#processors.groups.GroupsProcessor.get_default_config_key)


            * [`GroupsProcessor.process()`](processors.md#processors.groups.GroupsProcessor.process)


    * [processors.loadbalancing module](processors.md#module-processors.loadbalancing)


        * [`LoadbalancingOperationFailed`](processors.md#processors.loadbalancing.LoadbalancingOperationFailed)


        * [`LoadbalancingProcessor`](processors.md#processors.loadbalancing.LoadbalancingProcessor)


            * [`LoadbalancingProcessor.get_backend()`](processors.md#processors.loadbalancing.LoadbalancingProcessor.get_backend)


            * [`LoadbalancingProcessor.get_default_config_key()`](processors.md#processors.loadbalancing.LoadbalancingProcessor.get_default_config_key)


            * [`LoadbalancingProcessor.get_region_backend()`](processors.md#processors.loadbalancing.LoadbalancingProcessor.get_region_backend)


            * [`LoadbalancingProcessor.process()`](processors.md#processors.loadbalancing.LoadbalancingProcessor.process)


            * [`LoadbalancingProcessor.wait_for_operation_done()`](processors.md#processors.loadbalancing.LoadbalancingProcessor.wait_for_operation_done)


    * [processors.logging module](processors.md#module-processors.logging)


        * [`LoggingProcessor`](processors.md#processors.logging.LoggingProcessor)


            * [`LoggingProcessor.get_default_config_key()`](processors.md#processors.logging.LoggingProcessor.get_default_config_key)


            * [`LoggingProcessor.process()`](processors.md#processors.logging.LoggingProcessor.process)


    * [processors.monitoring module](processors.md#module-processors.monitoring)


        * [`MonitoringProcessor`](processors.md#processors.monitoring.MonitoringProcessor)


            * [`MonitoringProcessor.get_default_config_key()`](processors.md#processors.monitoring.MonitoringProcessor.get_default_config_key)


            * [`MonitoringProcessor.process()`](processors.md#processors.monitoring.MonitoringProcessor.process)


    * [processors.opsgenie module](processors.md#module-processors.opsgenie)


        * [`OpsgenieProcessor`](processors.md#processors.opsgenie.OpsgenieProcessor)


            * [`OpsgenieProcessor.get_default_config_key()`](processors.md#processors.opsgenie.OpsgenieProcessor.get_default_config_key)


            * [`OpsgenieProcessor.process()`](processors.md#processors.opsgenie.OpsgenieProcessor.process)


    * [processors.projects module](processors.md#module-processors.projects)


        * [`ProjectsProcessor`](processors.md#processors.projects.ProjectsProcessor)


            * [`ProjectsProcessor.get_default_config_key()`](processors.md#processors.projects.ProjectsProcessor.get_default_config_key)


            * [`ProjectsProcessor.process()`](processors.md#processors.projects.ProjectsProcessor.process)


    * [processors.recommendations module](processors.md#module-processors.recommendations)


        * [`RecommendationsProcessor`](processors.md#processors.recommendations.RecommendationsProcessor)


            * [`RecommendationsProcessor.get_default_config_key()`](processors.md#processors.recommendations.RecommendationsProcessor.get_default_config_key)


            * [`RecommendationsProcessor.get_insights()`](processors.md#processors.recommendations.RecommendationsProcessor.get_insights)


            * [`RecommendationsProcessor.get_link()`](processors.md#processors.recommendations.RecommendationsProcessor.get_link)


            * [`RecommendationsProcessor.get_recommendations()`](processors.md#processors.recommendations.RecommendationsProcessor.get_recommendations)


            * [`RecommendationsProcessor.get_regions()`](processors.md#processors.recommendations.RecommendationsProcessor.get_regions)


            * [`RecommendationsProcessor.get_zones()`](processors.md#processors.recommendations.RecommendationsProcessor.get_zones)


            * [`RecommendationsProcessor.insights`](processors.md#processors.recommendations.RecommendationsProcessor.insights)


            * [`RecommendationsProcessor.is_billing_account()`](processors.md#processors.recommendations.RecommendationsProcessor.is_billing_account)


            * [`RecommendationsProcessor.is_folder()`](processors.md#processors.recommendations.RecommendationsProcessor.is_folder)


            * [`RecommendationsProcessor.is_global()`](processors.md#processors.recommendations.RecommendationsProcessor.is_global)


            * [`RecommendationsProcessor.is_multi_region()`](processors.md#processors.recommendations.RecommendationsProcessor.is_multi_region)


            * [`RecommendationsProcessor.is_organization()`](processors.md#processors.recommendations.RecommendationsProcessor.is_organization)


            * [`RecommendationsProcessor.is_project()`](processors.md#processors.recommendations.RecommendationsProcessor.is_project)


            * [`RecommendationsProcessor.is_region()`](processors.md#processors.recommendations.RecommendationsProcessor.is_region)


            * [`RecommendationsProcessor.is_zone()`](processors.md#processors.recommendations.RecommendationsProcessor.is_zone)


            * [`RecommendationsProcessor.multi_regions`](processors.md#processors.recommendations.RecommendationsProcessor.multi_regions)


            * [`RecommendationsProcessor.process()`](processors.md#processors.recommendations.RecommendationsProcessor.process)


            * [`RecommendationsProcessor.recommenders`](processors.md#processors.recommendations.RecommendationsProcessor.recommenders)


            * [`RecommendationsProcessor.rollup_insights()`](processors.md#processors.recommendations.RecommendationsProcessor.rollup_insights)


            * [`RecommendationsProcessor.rollup_recommendations()`](processors.md#processors.recommendations.RecommendationsProcessor.rollup_recommendations)


        * [`UnknownRecommenderException`](processors.md#processors.recommendations.UnknownRecommenderException)


    * [processors.scc module](processors.md#module-processors.scc)


        * [`SccProcessor`](processors.md#processors.scc.SccProcessor)


            * [`SccProcessor.get_default_config_key()`](processors.md#processors.scc.SccProcessor.get_default_config_key)


            * [`SccProcessor.process()`](processors.md#processors.scc.SccProcessor.process)


    * [processors.secret module](processors.md#module-processors.secret)


        * [`SecretProcessor`](processors.md#processors.secret.SecretProcessor)


            * [`SecretProcessor.get_default_config_key()`](processors.md#processors.secret.SecretProcessor.get_default_config_key)


            * [`SecretProcessor.process()`](processors.md#processors.secret.SecretProcessor.process)


    * [processors.setvariable module](processors.md#module-processors.setvariable)


        * [`SetvariableProcessor`](processors.md#processors.setvariable.SetvariableProcessor)


            * [`SetvariableProcessor.get_default_config_key()`](processors.md#processors.setvariable.SetvariableProcessor.get_default_config_key)


            * [`SetvariableProcessor.process()`](processors.md#processors.setvariable.SetvariableProcessor.process)


    * [processors.shellscript module](processors.md#module-processors.shellscript)


        * [`CommandFailedException`](processors.md#processors.shellscript.CommandFailedException)


        * [`ShellscriptProcessor`](processors.md#processors.shellscript.ShellscriptProcessor)


            * [`ShellscriptProcessor.get_default_config_key()`](processors.md#processors.shellscript.ShellscriptProcessor.get_default_config_key)


            * [`ShellscriptProcessor.process()`](processors.md#processors.shellscript.ShellscriptProcessor.process)


    * [processors.slack module](processors.md#module-processors.slack)


        * [`SlackProcessor`](processors.md#processors.slack.SlackProcessor)


            * [`SlackProcessor.call_slack()`](processors.md#processors.slack.SlackProcessor.call_slack)


            * [`SlackProcessor.get_default_config_key()`](processors.md#processors.slack.SlackProcessor.get_default_config_key)


            * [`SlackProcessor.process()`](processors.md#processors.slack.SlackProcessor.process)


    * [processors.storage module](processors.md#module-processors.storage)


        * [`StorageProcessor`](processors.md#processors.storage.StorageProcessor)


            * [`StorageProcessor.get_default_config_key()`](processors.md#processors.storage.StorageProcessor.get_default_config_key)


            * [`StorageProcessor.process()`](processors.md#processors.storage.StorageProcessor.process)


    * [processors.transcode module](processors.md#module-processors.transcode)


        * [`InvalidModeException`](processors.md#processors.transcode.InvalidModeException)


        * [`TranscodeProcessor`](processors.md#processors.transcode.TranscodeProcessor)


            * [`TranscodeProcessor.get_default_config_key()`](processors.md#processors.transcode.TranscodeProcessor.get_default_config_key)


            * [`TranscodeProcessor.process()`](processors.md#processors.transcode.TranscodeProcessor.process)


    * [processors.vertexgenai module](processors.md#module-processors.vertexgenai)


        * [`VertexgenaiProcessor`](processors.md#processors.vertexgenai.VertexgenaiProcessor)


            * [`VertexgenaiProcessor.get_default_config_key()`](processors.md#processors.vertexgenai.VertexgenaiProcessor.get_default_config_key)


            * [`VertexgenaiProcessor.process()`](processors.md#processors.vertexgenai.VertexgenaiProcessor.process)


    * [Module contents](processors.md#module-processors)


* [test package](test.md)


    * [Submodules](test.md#submodules)


    * [test.helpers module](test.md#module-test.helpers)


        * [`fixture_to_pubsub()`](test.md#test.helpers.fixture_to_pubsub)


        * [`load_config()`](test.md#test.helpers.load_config)


    * [test.test_filters module](test.md#module-test.test_filters)


        * [`TestFilters`](test.md#test.test_filters.TestFilters)


            * [`TestFilters.test_filters()`](test.md#test.test_filters.TestFilters.test_filters)


    * [test.test_handling module](test.md#module-test.test_handling)


        * [`TestHandling`](test.md#test.test_handling.TestHandling)


            * [`TestHandling.test_handling()`](test.md#test.test_handling.TestHandling.test_handling)


    * [test.test_ingcp module](test.md#module-test.test_ingcp)


        * [`TestIngcp`](test.md#test.test_ingcp.TestIngcp)


            * [`TestIngcp.test_in_gcp()`](test.md#test.test_ingcp.TestIngcp.test_in_gcp)


    * [test.test_macros module](test.md#module-test.test_macros)


        * [`TestMacros`](test.md#test.test_macros.TestMacros)


            * [`TestMacros.test_macros()`](test.md#test.test_macros.TestMacros.test_macros)


    * [test.test_mail_msgraphapi module](test.md#module-test.test_mail_msgraphapi)


        * [`TestMailMsGraphAPI`](test.md#test.test_mail_msgraphapi.TestMailMsGraphAPI)


            * [`TestMailMsGraphAPI.test_fetch_ms_access_token()`](test.md#test.test_mail_msgraphapi.TestMailMsGraphAPI.test_fetch_ms_access_token)


            * [`TestMailMsGraphAPI.test_send()`](test.md#test.test_mail_msgraphapi.TestMailMsGraphAPI.test_send)


    * [test.test_pubsub module](test.md#module-test.test_pubsub)


        * [`TestPubsub`](test.md#test.test_pubsub.TestPubsub)


            * [`TestPubsub.message`](test.md#test.test_pubsub.TestPubsub.message)


            * [`TestPubsub.message_sent`](test.md#test.test_pubsub.TestPubsub.message_sent)


            * [`TestPubsub.test_message_is_not_too_old()`](test.md#test.test_pubsub.TestPubsub.test_message_is_not_too_old)


            * [`TestPubsub.test_message_too_old()`](test.md#test.test_pubsub.TestPubsub.test_message_too_old)


    * [test.test_resend module](test.md#module-test.test_resend)


        * [`TestResend`](test.md#test.test_resend.TestResend)


            * [`TestResend.test_resend()`](test.md#test.test_resend.TestResend.test_resend)


    * [test.test_sendgrid module](test.md#module-test.test_sendgrid)


        * [`TestSendgrid`](test.md#test.test_sendgrid.TestSendgrid)


            * [`TestSendgrid.test_sendgrid()`](test.md#test.test_sendgrid.TestSendgrid.test_sendgrid)


    * [test.test_shellscript module](test.md#module-test.test_shellscript)


        * [`TestShellscript`](test.md#test.test_shellscript.TestShellscript)


            * [`TestShellscript.test_shellscript_fail()`](test.md#test.test_shellscript.TestShellscript.test_shellscript_fail)


            * [`TestShellscript.test_shellscript_succeed()`](test.md#test.test_shellscript.TestShellscript.test_shellscript_succeed)


    * [Module contents](test.md#module-test)
