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


        * [`regex_replace()`](filters.md#filters.regex.regex_replace)


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


        * [`make_list()`](filters.md#filters.strings.make_list)


        * [`re_escape()`](filters.md#filters.strings.re_escape)


        * [`read_gcs_object()`](filters.md#filters.strings.read_gcs_object)


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


            * [`BaseHelper.jinja_environment`](helpers.md#helpers.base.BaseHelper.jinja_environment)


            * [`BaseHelper.logger`](helpers.md#helpers.base.BaseHelper.logger)


            * [`BaseHelper.project_number_cache`](helpers.md#helpers.base.BaseHelper.project_number_cache)


        * [`NoCredentialsException`](helpers.md#helpers.base.NoCredentialsException)


        * [`get_branded_http()`](helpers.md#helpers.base.get_branded_http)


        * [`get_grpc_client_info()`](helpers.md#helpers.base.get_grpc_client_info)


        * [`get_user_agent()`](helpers.md#helpers.base.get_user_agent)


    * [Module contents](helpers.md#module-helpers)


* [main module](main.md)


    * [`CloudRunServer`](main.md#main.CloudRunServer)


        * [`CloudRunServer.on_get()`](main.md#main.CloudRunServer.on_get)


        * [`CloudRunServer.on_post()`](main.md#main.CloudRunServer.on_post)


    * [`InvalidMessageFormatException`](main.md#main.InvalidMessageFormatException)


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


    * [`get_jinja_environment()`](main.md#main.get_jinja_environment)


    * [`get_jinja_escaping()`](main.md#main.get_jinja_escaping)


    * [`handle_ignore_on()`](main.md#main.handle_ignore_on)


    * [`load_configuration()`](main.md#main.load_configuration)


    * [`process_message()`](main.md#main.process_message)


    * [`process_message_legacy()`](main.md#main.process_message_legacy)


    * [`process_message_pipeline()`](main.md#main.process_message_pipeline)


    * [`process_pubsub()`](main.md#main.process_pubsub)


    * [`run_webserver()`](main.md#main.run_webserver)


    * [`setup_logging()`](main.md#main.setup_logging)


* [output package](output.md)


    * [Submodules](output.md#submodules)


    * [output.base module](output.md#module-output.base)


        * [`NotConfiguredException`](output.md#output.base.NotConfiguredException)


        * [`Output`](output.md#output.base.Output)


            * [`Output.config`](output.md#output.base.Output.config)


            * [`Output.context`](output.md#output.base.Output.context)


            * [`Output.data`](output.md#output.base.Output.data)


            * [`Output.event`](output.md#output.base.Output.event)


            * [`Output.output()`](output.md#output.base.Output.output)


            * [`Output.output_config`](output.md#output.base.Output.output_config)


    * [output.bigquery module](output.md#module-output.bigquery)


        * [`BigqueryOutput`](output.md#output.bigquery.BigqueryOutput)


            * [`BigqueryOutput.context`](output.md#output.bigquery.BigqueryOutput.context)


            * [`BigqueryOutput.output()`](output.md#output.bigquery.BigqueryOutput.output)


        * [`InvalidJobOptionException`](output.md#output.bigquery.InvalidJobOptionException)


    * [output.delay module](output.md#module-output.delay)


        * [`DelayOutput`](output.md#output.delay.DelayOutput)


            * [`DelayOutput.context`](output.md#output.delay.DelayOutput.context)


            * [`DelayOutput.output()`](output.md#output.delay.DelayOutput.output)


    * [output.gcs module](output.md#module-output.gcs)


        * [`GcsOutput`](output.md#output.gcs.GcsOutput)


            * [`GcsOutput.context`](output.md#output.gcs.GcsOutput.context)


            * [`GcsOutput.output()`](output.md#output.gcs.GcsOutput.output)


    * [output.gcscopy module](output.md#module-output.gcscopy)


        * [`GcscopyOutput`](output.md#output.gcscopy.GcscopyOutput)


            * [`GcscopyOutput.context`](output.md#output.gcscopy.GcscopyOutput.context)


            * [`GcscopyOutput.output()`](output.md#output.gcscopy.GcscopyOutput.output)


    * [output.groupssettings module](output.md#module-output.groupssettings)


        * [`GroupssettingsOutput`](output.md#output.groupssettings.GroupssettingsOutput)


            * [`GroupssettingsOutput.context`](output.md#output.groupssettings.GroupssettingsOutput.context)


            * [`GroupssettingsOutput.output()`](output.md#output.groupssettings.GroupssettingsOutput.output)


    * [output.logger module](output.md#module-output.logger)


        * [`LoggerOutput`](output.md#output.logger.LoggerOutput)


            * [`LoggerOutput.context`](output.md#output.logger.LoggerOutput.context)


            * [`LoggerOutput.output()`](output.md#output.logger.LoggerOutput.output)


    * [output.mail module](output.md#module-output.mail)


        * [`AllTransportsFailedException`](output.md#output.mail.AllTransportsFailedException)


        * [`DownloadFailedException`](output.md#output.mail.DownloadFailedException)


        * [`GroupNotFoundException`](output.md#output.mail.GroupNotFoundException)


        * [`InvalidSchemeException`](output.md#output.mail.InvalidSchemeException)


        * [`MailOutput`](output.md#output.mail.MailOutput)


            * [`MailOutput.context`](output.md#output.mail.MailOutput.context)


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


            * [`PubsubOutput.context`](output.md#output.pubsub.PubsubOutput.context)


            * [`PubsubOutput.output()`](output.md#output.pubsub.PubsubOutput.output)


    * [output.scc module](output.md#module-output.scc)


        * [`SccOutput`](output.md#output.scc.SccOutput)


            * [`SccOutput.context`](output.md#output.scc.SccOutput.context)


            * [`SccOutput.output()`](output.md#output.scc.SccOutput.output)


    * [output.test module](output.md#module-output.test)


        * [`TestFailedException`](output.md#output.test.TestFailedException)


        * [`TestOutput`](output.md#output.test.TestOutput)


            * [`TestOutput.context`](output.md#output.test.TestOutput.context)


            * [`TestOutput.output()`](output.md#output.test.TestOutput.output)


    * [output.twilio module](output.md#module-output.twilio)


        * [`TwilioOutput`](output.md#output.twilio.TwilioOutput)


            * [`TwilioOutput.context`](output.md#output.twilio.TwilioOutput.context)


            * [`TwilioOutput.output()`](output.md#output.twilio.TwilioOutput.output)


    * [output.webhook module](output.md#module-output.webhook)


        * [`WebhookOutput`](output.md#output.webhook.WebhookOutput)


            * [`WebhookOutput.context`](output.md#output.webhook.WebhookOutput.context)


            * [`WebhookOutput.output()`](output.md#output.webhook.WebhookOutput.output)


    * [Module contents](output.md#module-output)


* [processors package](processors.md)


    * [Submodules](processors.md#submodules)


    * [processors.base module](processors.md#module-processors.base)


        * [`NoConfigKeySetException`](processors.md#processors.base.NoConfigKeySetException)


        * [`NotConfiguredException`](processors.md#processors.base.NotConfiguredException)


        * [`Processor`](processors.md#processors.base.Processor)


            * [`Processor.config`](processors.md#processors.base.Processor.config)


            * [`Processor.context`](processors.md#processors.base.Processor.context)


            * [`Processor.data`](processors.md#processors.base.Processor.data)


            * [`Processor.event`](processors.md#processors.base.Processor.event)


            * [`Processor.expand_projects()`](processors.md#processors.base.Processor.expand_projects)


            * [`Processor.get_default_config_key()`](processors.md#processors.base.Processor.get_default_config_key)


            * [`Processor.process()`](processors.md#processors.base.Processor.process)


        * [`UnknownProjectException`](processors.md#processors.base.UnknownProjectException)


    * [processors.bigquery module](processors.md#module-processors.bigquery)


        * [`BigqueryProcessor`](processors.md#processors.bigquery.BigqueryProcessor)


            * [`BigqueryProcessor.context`](processors.md#processors.bigquery.BigqueryProcessor.context)


            * [`BigqueryProcessor.get_default_config_key()`](processors.md#processors.bigquery.BigqueryProcessor.get_default_config_key)


            * [`BigqueryProcessor.process()`](processors.md#processors.bigquery.BigqueryProcessor.process)


    * [processors.budget module](processors.md#module-processors.budget)


        * [`BudgetProcessor`](processors.md#processors.budget.BudgetProcessor)


            * [`BudgetProcessor.context`](processors.md#processors.budget.BudgetProcessor.context)


            * [`BudgetProcessor.get_default_config_key()`](processors.md#processors.budget.BudgetProcessor.get_default_config_key)


            * [`BudgetProcessor.process()`](processors.md#processors.budget.BudgetProcessor.process)


        * [`MissingAttributesException`](processors.md#processors.budget.MissingAttributesException)


    * [processors.cai module](processors.md#module-processors.cai)


        * [`CaiProcessor`](processors.md#processors.cai.CaiProcessor)


            * [`CaiProcessor.context`](processors.md#processors.cai.CaiProcessor.context)


            * [`CaiProcessor.get_default_config_key()`](processors.md#processors.cai.CaiProcessor.get_default_config_key)


            * [`CaiProcessor.process()`](processors.md#processors.cai.CaiProcessor.process)


    * [processors.directory module](processors.md#module-processors.directory)


        * [`DirectoryProcessor`](processors.md#processors.directory.DirectoryProcessor)


            * [`DirectoryProcessor.context`](processors.md#processors.directory.DirectoryProcessor.context)


            * [`DirectoryProcessor.get_default_config_key()`](processors.md#processors.directory.DirectoryProcessor.get_default_config_key)


            * [`DirectoryProcessor.process()`](processors.md#processors.directory.DirectoryProcessor.process)


    * [processors.genericjson module](processors.md#module-processors.genericjson)


        * [`GenericjsonProcessor`](processors.md#processors.genericjson.GenericjsonProcessor)


            * [`GenericjsonProcessor.context`](processors.md#processors.genericjson.GenericjsonProcessor.context)


            * [`GenericjsonProcessor.get_default_config_key()`](processors.md#processors.genericjson.GenericjsonProcessor.get_default_config_key)


            * [`GenericjsonProcessor.process()`](processors.md#processors.genericjson.GenericjsonProcessor.process)


    * [processors.groups module](processors.md#module-processors.groups)


        * [`GroupsProcessor`](processors.md#processors.groups.GroupsProcessor)


            * [`GroupsProcessor.context`](processors.md#processors.groups.GroupsProcessor.context)


            * [`GroupsProcessor.get_default_config_key()`](processors.md#processors.groups.GroupsProcessor.get_default_config_key)


            * [`GroupsProcessor.process()`](processors.md#processors.groups.GroupsProcessor.process)


    * [processors.monitoring module](processors.md#module-processors.monitoring)


        * [`MonitoringProcessor`](processors.md#processors.monitoring.MonitoringProcessor)


            * [`MonitoringProcessor.context`](processors.md#processors.monitoring.MonitoringProcessor.context)


            * [`MonitoringProcessor.get_default_config_key()`](processors.md#processors.monitoring.MonitoringProcessor.get_default_config_key)


            * [`MonitoringProcessor.process()`](processors.md#processors.monitoring.MonitoringProcessor.process)


    * [processors.projects module](processors.md#module-processors.projects)


        * [`ProjectsProcessor`](processors.md#processors.projects.ProjectsProcessor)


            * [`ProjectsProcessor.context`](processors.md#processors.projects.ProjectsProcessor.context)


            * [`ProjectsProcessor.get_default_config_key()`](processors.md#processors.projects.ProjectsProcessor.get_default_config_key)


            * [`ProjectsProcessor.process()`](processors.md#processors.projects.ProjectsProcessor.process)


    * [processors.recommendations module](processors.md#module-processors.recommendations)


        * [`RecommendationsProcessor`](processors.md#processors.recommendations.RecommendationsProcessor)


            * [`RecommendationsProcessor.context`](processors.md#processors.recommendations.RecommendationsProcessor.context)


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


            * [`SccProcessor.context`](processors.md#processors.scc.SccProcessor.context)


            * [`SccProcessor.get_default_config_key()`](processors.md#processors.scc.SccProcessor.get_default_config_key)


            * [`SccProcessor.process()`](processors.md#processors.scc.SccProcessor.process)


    * [processors.shellscript module](processors.md#module-processors.shellscript)


        * [`CommandFailedException`](processors.md#processors.shellscript.CommandFailedException)


        * [`ShellscriptProcessor`](processors.md#processors.shellscript.ShellscriptProcessor)


            * [`ShellscriptProcessor.context`](processors.md#processors.shellscript.ShellscriptProcessor.context)


            * [`ShellscriptProcessor.get_default_config_key()`](processors.md#processors.shellscript.ShellscriptProcessor.get_default_config_key)


            * [`ShellscriptProcessor.process()`](processors.md#processors.shellscript.ShellscriptProcessor.process)


    * [processors.storage module](processors.md#module-processors.storage)


        * [`StorageProcessor`](processors.md#processors.storage.StorageProcessor)


            * [`StorageProcessor.context`](processors.md#processors.storage.StorageProcessor.context)


            * [`StorageProcessor.get_default_config_key()`](processors.md#processors.storage.StorageProcessor.get_default_config_key)


            * [`StorageProcessor.process()`](processors.md#processors.storage.StorageProcessor.process)


    * [processors.transcode module](processors.md#module-processors.transcode)


        * [`InvalidModeException`](processors.md#processors.transcode.InvalidModeException)


        * [`TranscodeProcessor`](processors.md#processors.transcode.TranscodeProcessor)


            * [`TranscodeProcessor.context`](processors.md#processors.transcode.TranscodeProcessor.context)


            * [`TranscodeProcessor.get_default_config_key()`](processors.md#processors.transcode.TranscodeProcessor.get_default_config_key)


            * [`TranscodeProcessor.process()`](processors.md#processors.transcode.TranscodeProcessor.process)


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
