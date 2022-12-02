# output package

## Submodules

## output.base module


### _exception_ output.base.NotConfiguredException()
Bases: `Exception`


### _class_ output.base.Output(config, output_config, jinja_environment, data, event, context)
Bases: [`BaseHelper`](helpers.md#helpers.base.BaseHelper)


#### config(_ = Non_ )

#### context(_: Contex_ )

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



#### context(_: Contex_ )

#### output()

### _exception_ output.bigquery.InvalidJobOptionException()
Bases: `Exception`

## output.gcs module


### _class_ output.gcs.GcsOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### context(_: Contex_ )

#### output()
## output.gcscopy module


### _class_ output.gcscopy.GcscopyOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### context(_: Contex_ )

#### output()
## output.groupssettings module


### _class_ output.groupssettings.GroupssettingsOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### context(_: Contex_ )

#### output()
## output.logger module


### _class_ output.logger.LoggerOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### context(_: Contex_ )

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


#### context(_: Contex_ )

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

#### context(_: Contex_ )

#### output()
## output.scc module


### _class_ output.scc.SccOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### context(_: Contex_ )

#### output()
## output.test module


### _exception_ output.test.TestFailedException()
Bases: `Exception`


### _class_ output.test.TestOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### context(_: Contex_ )

#### output()
## output.twilio module


### _class_ output.twilio.TwilioOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### context(_: Contex_ )

#### output()
## output.webhook module


### _class_ output.webhook.WebhookOutput(config, output_config, jinja_environment, data, event, context)
Bases: `Output`


#### context(_: Contex_ )

#### output()
## Module contents
