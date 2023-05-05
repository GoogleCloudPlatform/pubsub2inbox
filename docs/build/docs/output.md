# output package

## Submodules

## output.base module


### _exception_ output.base.NotConfiguredException()
Bases: `Exception`


### _class_ output.base.Output(config, output_config, jinja_environment, data, event, context)
Bases: [`BaseHelper`](helpers.md#helpers.base.BaseHelper)


#### config(_ = Non_ )

#### context(_: [`Context`](helpers.md#helpers.base.Context_ )

#### data(_ = Non_ )

#### event(_ = Non_ )

#### _abstract_ output()

#### output_config(_ = Non_ )
## output.bigquery module


### _class_ output.bigquery.BigqueryOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`

BigQuery output processors can write data into BigQuery tables.


* **Parameters**

    
    * **datasetWithTable** (*str*) – BigQuery table in “dataset.table” notation.


    * **source** (*str*) – Source file on Cloud Storage to load the file from (in “gs://bucket/file” format).


    * **location** (*str*) – Dataset location (eg. “europe-west4”)


    * **job** (*dict**, **optional*) – Job configuration, eg. skipLeadingRows, see: [https://cloud.google.com/bigquery/docs/reference/rest/v2/Job#JobConfigurationLoad](https://cloud.google.com/bigquery/docs/reference/rest/v2/Job#JobConfigurationLoad)


    * **project** (*str**, **optional*) – Google Cloud project to issue BigQuery API calls against.



#### output()

### _exception_ output.bigquery.InvalidJobOptionException()
Bases: `Exception`

## output.chat module


### _class_ output.chat.ChatOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`

Sends message to a Google Chat space.


* **Parameters**

    
    * **serviceAccountEmail** (*str*) – A service account email for which a scoped token will be requested.
    You should invite this service account to the space. The Cloud Functions has to has Service
    Account Token Creator to this service account. Can also be specified via SERVICE_ACCOUNT
    environment variable.


    * **parent** (*str*) – A Google Chat space (spaces/XYZ).


    * **message** (*dict*) – A Message object (see: [https://developers.google.com/chat/api/reference/rest/v1/spaces.messages#Message](https://developers.google.com/chat/api/reference/rest/v1/spaces.messages#Message)).


    * **project** (*str**, **optional*) – Google Cloud project to issue Chat API calls against.



#### output()
## output.delay module


### _class_ output.delay.DelayOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### output()
## output.gcs module


### _class_ output.gcs.GcsOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### output()
## output.gcscopy module


### _class_ output.gcscopy.GcscopyOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### output()
## output.groupssettings module


### _class_ output.groupssettings.GroupssettingsOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### output()
## output.logger module


### _class_ output.logger.LoggerOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### output()
## output.mail module


### _exception_ output.mail.AllTransportsFailedException()
Bases: `Exception`


### _exception_ output.mail.DownloadFailedException()
Bases: `Exception`


### _exception_ output.mail.GroupNotFoundException()
Bases: `Exception`


### _exception_ output.mail.InvalidSchemeException()
Bases: `Exception`


### _class_ output.mail.MailOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### embed_images(config)

#### expand_recipients(mail, config)
Expands group recipients using the Directory API


#### output()

#### send_via_msgraphapi(transport, mail, embedded_images, config)

#### send_via_sendgrid(transport, mail, embedded_images, config)

#### send_via_smtp(transport, mail, embedded_images, config)

### _exception_ output.mail.MultipleSendersException()
Bases: `Exception`


### _exception_ output.mail.OAuthTokenFetchException()
Bases: `Exception`

## output.pubsub module


### _class_ output.pubsub.PubsubOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### callback(future)

#### output()
## output.scc module


### _class_ output.scc.SccOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### output()
## output.test module


### _exception_ output.test.TestFailedException()
Bases: `Exception`


### _class_ output.test.TestOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### output()
## output.twilio module


### _class_ output.twilio.TwilioOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### output()
## output.webhook module


### _class_ output.webhook.WebhookOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### output()
## Module contents
