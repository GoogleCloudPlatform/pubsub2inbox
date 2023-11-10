# main module


### _class_ main.CloudRunServer()
Bases: `object`


#### on_get(req, res)

#### on_post(req, res)

### _exception_ main.InvalidMessageFormatException()
Bases: `Exception`


### _exception_ main.MalformedGlobalsException()
Bases: `Exception`


### _exception_ main.MalformedMacrosException()
Bases: `Exception`


### _exception_ main.MalformedTypeInPipelineException()
Bases: `Exception`


### _exception_ main.MessageTooOldException()
Bases: `Exception`


### _exception_ main.NoDataFieldException()
Bases: `Exception`


### _exception_ main.NoMessageReceivedException()
Bases: `Exception`


### _exception_ main.NoOutputsConfiguredException()
Bases: `Exception`


### _exception_ main.NoPipelineConfiguredException()
Bases: `Exception`


### _exception_ main.NoResendConfigException()
Bases: `Exception`


### _exception_ main.NoTypeConfiguredException()
Bases: `Exception`


### _exception_ main.NoTypeInPipelineException()
Bases: `Exception`


### main.check_retry_period(config, context, logger)

### main.decode_and_process(logger, config, event, context)

### main.get_jinja_environment()

### main.get_jinja_escaping(template_name)

### main.handle_ignore_on(logger, ignore_config, jinja_environment, template_variables)

### main.load_configuration(file_name)

### main.macro_helper(macro_func, \*args, \*\*kwargs)

### main.process_message(config, data, event, context)

### main.process_message_legacy(logger, config, data, event, context)

### main.process_message_pipeline(logger, config, data, event, context)

### main.process_pubsub(event, context, message_too_old_exception=False)
Function that is triggered by Pub/Sub incoming message.
:type event: 
:param event: The dictionary with data specific to this type of
:type event: dict
:param event. The data field contains the PubsubMessage message. The:
:param attributes field will contain custom attributes if there are any.:
:type context: 
:param context: The Cloud Functions event
:type context: google.cloud.functions.Context
:param metadata. The event_id field contains the Pub/Sub message ID. The:
:param timestamp field contains the publish time.:


### main.process_pubsub_v2(event, context, message_too_old_exception=False)
Function that is triggered by Pub/Sub incoming message for functions V2.
:type event: 
:param event: The dictionary with data specific to this type of
:type event: dict
:param event. The data field contains the PubsubMessage message. The:
:param attributes field will contain custom attributes if there are any.:
:type context: 
:param context: The Cloud Functions event
:type context: google.cloud.functions.Context
:param metadata. The event_id field contains the Pub/Sub message ID. The:
:param timestamp field contains the publish time.:


### main.run_webserver(run_locally=False)

### main.setup_logging()
