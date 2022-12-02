# main module


### _class_ main.CloudRunServer()
Bases: `object`


#### on_get(req, res)

#### on_post(req, res)

### _exception_ main.InvalidMessageFormatException()
Bases: `Exception`


### _exception_ main.MessageTooOldException()
Bases: `Exception`


### _exception_ main.NoDataFieldException()
Bases: `Exception`


### _exception_ main.NoMessageReceivedException()
Bases: `Exception`


### _exception_ main.NoOutputsConfiguredException()
Bases: `Exception`


### _exception_ main.NoResendConfigException()
Bases: `Exception`


### _exception_ main.NoTypeConfiguredException()
Bases: `Exception`


### main.decode_and_process(logger, config, event, context)

### main.get_jinja_environment()

### main.get_jinja_escaping(template_name)

### main.load_configuration(file_name)

### main.process_message(config, data, event, context)

### main.process_pubsub(event, context, message_too_old_exception=False)
Function that is triggered by Pub/Sub incoming message.
:param event: The dictionary with data specific to this type of
:type event: dict
:param event. The data field contains the PubsubMessage message. The:
:param attributes field will contain custom attributes if there are any.:
:param context: The Cloud Functions event
:type context: google.cloud.functions.Context
:param metadata. The event_id field contains the Pub/Sub message ID. The:
:param timestamp field contains the publish time.:


### main.run_webserver(run_locally=False)

### main.setup_logging()
