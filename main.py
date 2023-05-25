#!/usr/bin/env python3
#   Copyright 2022 Google LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import os
import base64
import yaml
import json
import argparse
import logging
import socket
import hashlib
from time import mktime
from datetime import datetime, timezone, timedelta
import parsedatetime
from dateutil import parser
from filters import get_jinja_filters, get_jinja_tests
from jinja2 import Environment, TemplateError
from google.cloud import secretmanager, storage
from pythonjsonlogger import jsonlogger
import traceback
from helpers.base import get_grpc_client_info, Context, BaseHelper
import random
import uuid
from functools import partial

config_file_name = 'config.yaml'
execution_count = 0
configuration = None
logger = None
extra_vars = []


def load_configuration(file_name):
    if os.getenv('CONFIG') and os.getenv('CONFIG') != '':
        logger = logging.getLogger('pubsub2inbox')
        secret_manager_url = os.getenv('CONFIG')
        if secret_manager_url.startswith('projects/'):
            logger.debug('Loading configuration from Secret Manager: %s' %
                         (secret_manager_url))
            client = secretmanager.SecretManagerServiceClient(
                client_info=get_grpc_client_info())
            response = client.access_secret_version(name=secret_manager_url)
            configuration = response.payload.data.decode('UTF-8')
        else:
            logger.debug('Loading configuration from bundled file: %s' %
                         (secret_manager_url))
            with open(secret_manager_url) as config_file:
                configuration = config_file.read()
    else:
        with open(file_name) as config_file:
            configuration = config_file.read()

    cfg = yaml.load(configuration, Loader=yaml.SafeLoader)
    return cfg


def get_jinja_escaping(template_name):
    if template_name and 'html' in template_name:
        return True
    return False


def get_jinja_environment():
    env = Environment(autoescape=get_jinja_escaping,
                      cache_size=0,
                      extensions=['jinja2.ext.do'])
    env.globals = {**env.globals, **{'env': os.environ}}
    env.globals['req_random_int'] = random.randrange(0, 9223372036854775807)
    request_uuid = uuid.uuid4()
    env.globals['req_random_uuid_hex'] = request_uuid.hex
    env.globals['req_random_uuid_int'] = request_uuid.int
    nice_uuid = base64.urlsafe_b64encode(request_uuid.bytes)
    env.globals['req_random_uuid'] = nice_uuid.decode('utf-8').rstrip(
        '=').lower(
        )  # This is not as unique as raw UUID, but still pretty unique

    if extra_vars and len(extra_vars) > 0:
        for v in extra_vars:
            if v[1].startswith('[') or v[1].startswith('{'):
                env.globals[v[0]] = json.loads(v[1])
            else:
                env.globals[v[0]] = v[1]
    env.filters.update(get_jinja_filters())
    env.tests.update(get_jinja_tests())
    return env


class MessageTooOldException(Exception):
    pass


class NoResendConfigException(Exception):
    pass


class NoTypeConfiguredException(Exception):
    pass


class NoOutputsConfiguredException(Exception):
    pass


class NoPipelineConfiguredException(Exception):
    pass


class NoTypeInPipelineException(Exception):
    pass


class MalformedTypeInPipelineException(Exception):
    pass


class NoDataFieldException(Exception):
    pass


class NoMessageReceivedException(Exception):
    pass


class InvalidMessageFormatException(Exception):
    pass


class MalformedGlobalsException(Exception):
    pass


class MalformedMacrosException(Exception):
    pass


def check_retry_period(config, context, logger):
    # Ignore messages submitted before our retry period
    retry_period = '2 days ago'
    if 'retryPeriod' in config:
        retry_period = config['retryPeriod']
    if 'maximumMessageAge' in config:
        retry_period = config['maximumMessageAge']
    if retry_period != 'skip':
        retry_period_parsed = parsedatetime.Calendar(
            version=parsedatetime.VERSION_CONTEXT_STYLE).parse(retry_period)
        if len(retry_period_parsed) > 1:
            retry_earliest = datetime.fromtimestamp(
                mktime(retry_period_parsed[0]), timezone.utc)
        else:
            retry_earliest = datetime.fromtimestamp(mktime(retry_period_parsed),
                                                    timezone.utc)
        message_time = parser.parse(context.timestamp)
        if (message_time - retry_earliest) < timedelta(0, 0):
            logger.warning(
                'Ignoring message because it\'s past the retry period.',
                extra={
                    'event_id': context.event_id,
                    'retry_period': retry_period,
                    'retry_earliest': retry_earliest.strftime('%c'),
                    'event_timestamp': message_time
                })
            raise MessageTooOldException(
                'Ignoring message because it\'s past the retry period.')


def process_message_legacy(logger, config, data, event, context):
    template_variables = {
        'data': data,
        'event': event,
        'context': context,
    }
    jinja_environment = get_jinja_environment()
    if 'processors' in config:
        for processor in config['processors']:
            config_key = None
            output_var = None
            if isinstance(processor, dict):
                config_key = processor[
                    'config'] if 'config' in processor else None
                if config_key:
                    # Expand config key if it's a Jinja expression
                    config_key_template = jinja_environment.from_string(
                        config_key)
                    config_key_template.name = 'config'
                    config_key = config_key_template.render()

                output_var = processor[
                    'output'] if 'output' in processor else None
                if output_var:
                    if isinstance(output_var, str):
                        # Expand output variable if it's a Jinja expression
                        output_var_template = jinja_environment.from_string(
                            output_var)
                        output_var_template.name = 'output'
                        output_var = output_var_template.render()
                    elif isinstance(output_var, dict):
                        new_output_var = {}
                        for k, v in output_var.items():
                            output_var_template = jinja_environment.from_string(
                                v)
                            output_var_template.name = 'output'
                            new_output_var[k] = output_var_template.render()
                        output_var = new_output_var

                processor = processor['processor']

            logger.debug('Processing message using input processor: %s' %
                         processor)
            mod = __import__('processors.%s' % processor)
            processor_module = getattr(mod, processor)
            processor_class = getattr(processor_module,
                                      '%sProcessor' % processor.capitalize())
            if not config_key:
                config_key = processor_class.get_default_config_key()

            processor_config = {}
            if config_key in config:
                processor_config = config[config_key]

            processor_instance = processor_class(processor_config,
                                                 jinja_environment, data, event,
                                                 context)

            if output_var:
                processor_variables = processor_instance.process(
                    output_var=output_var)
            else:
                processor_variables = processor_instance.process()
            template_variables.update(processor_variables)
            jinja_environment.globals = {
                **jinja_environment.globals,
                **template_variables
            }

    if 'processIf' in config:
        processif_template = jinja_environment.from_string(config['processIf'])
        processif_template.name = 'processif'
        processif_contents = processif_template.render()
        if processif_contents.strip() == '':
            logger.info(
                'Will not send message because processIf evaluated to empty.')
            return

    if 'resendBucket' in config:
        if 'resendPeriod' not in config:
            raise NoResendConfigException(
                'No resendPeriod configured, even though resendBucket is set!')

        resend_key_hash = hashlib.sha256()
        if 'resendKey' not in config:
            default_resend_key = template_variables.copy()
            default_resend_key.pop('context')
            resend_key_hash.update(
                json.dumps(default_resend_key).encode('utf-8'))
        else:
            key_template = jinja_environment.from_string(config['resendKey'])
            key_template.name = 'resend'
            key_contents = key_template.render()
            resend_key_hash.update(key_contents.encode('utf-8'))

        resend_file = resend_key_hash.hexdigest()
        logger.debug('Checking for resend object in bucket...',
                     extra={
                         'bucket': config['resendBucket'],
                         'blob': resend_file
                     })

        storage_client = storage.Client(client_info=get_grpc_client_info())
        bucket = storage_client.bucket(config['resendBucket'])
        resend_blob = bucket.blob(resend_file)
        if resend_blob.exists():
            resend_blob.reload()
            resend_period = config['resendPeriod']
            resend_period_parsed = parsedatetime.Calendar(
                version=parsedatetime.VERSION_CONTEXT_STYLE).parse(
                    resend_period, sourceTime=resend_blob.time_created)
            if len(resend_period_parsed) > 1:
                resend_earliest = datetime.fromtimestamp(
                    mktime(resend_period_parsed[0]))
            else:
                resend_earliest = datetime.fromtimestamp(
                    mktime(resend_period_parsed))

            if datetime.now() >= resend_earliest:
                logger.debug('Resending the message now.',
                             extra={
                                 'resend_earliest': resend_earliest,
                                 'blob_time_created': resend_blob.time_created
                             })
                resend_blob.upload_from_string('')
            else:
                logger.info(
                    'Can\'t resend the message now, resend period not elapsed.',
                    extra={
                        'resend_earliest': resend_earliest,
                        'blob_time_created': resend_blob.time_created
                    })
                return
        else:
            try:
                resend_blob.upload_from_string('', if_generation_match=0)
            except Exception as exc:
                # Handle TOCTOU condition
                if 'conditionNotMet' in str(exc):
                    logger.warning(
                        'Message (re)sending already in progress (resend key already exist).',
                        extra={'exception': exc})
                    return
                else:
                    raise exc
                return

    if 'outputs' in config:
        for output_config in config['outputs']:
            if 'type' not in output_config:
                raise NoTypeConfiguredException(
                    'No type configured for output!')

            if 'processIf' in output_config:
                processif_template = jinja_environment.from_string(
                    output_config['processIf'])
                processif_template.name = 'processif'
                processif_contents = processif_template.render()
                if processif_contents.strip() == '':
                    logger.info(
                        'Will not use output processor %s because processIf evaluated to empty.'
                        % output_config['type'])
                continue

            logger.debug('Processing message using output processor: %s' %
                         output_config['type'])

            output_type = output_config['type']
            mod = __import__('output.%s' % output_type)
            output_module = getattr(mod, output_type)
            output_class = getattr(output_module,
                                   '%sOutput' % output_type.capitalize())
            output_instance = output_class(config, output_config,
                                           jinja_environment, data, event,
                                           context)
            try:
                output_instance.output()
            except Exception as exc:
                if len(config['outputs']) > 1:
                    logger.error('Output processor %s failed, trying next...' %
                                 (output_type),
                                 extra={'exception': traceback.format_exc()})
                    if 'allOutputsMustSucceed' in config and config[
                            'allOutputsMustSucceed']:
                        raise exc
                else:
                    logger.error('Output processor %s failed.' % (output_type),
                                 extra={'exception': traceback.format_exc()})
                    raise exc

    else:
        raise NoOutputsConfiguredException('No outputs configured!')


def handle_ignore_on(logger, ignore_config, jinja_environment,
                     template_variables):
    if 'bucket' not in ignore_config:
        raise NoResendConfigException(
            'No Cloud Storage bucket configured, even though ignoreOn is set!')

    if 'period' not in ignore_config:
        raise NoResendConfigException(
            'No period configured, even though ignoreOn is set!')

    resend_key_hash = hashlib.sha256()
    if 'key' not in ignore_config:
        default_resend_key = template_variables.copy()
        default_resend_key.pop('context')
        resend_key_hash.update(json.dumps(default_resend_key).encode('utf-8'))
    else:
        key_template = jinja_environment.from_string(ignore_config['key'])
        key_template.name = 'resend'
        key_contents = key_template.render()
        resend_key_hash.update(key_contents.encode('utf-8'))

    resend_file = resend_key_hash.hexdigest()
    logger.debug('Checking for ignore object in bucket...',
                 extra={
                     'bucket': ignore_config['bucket'],
                     'blob': resend_file
                 })

    if os.getenv('STORAGE_EMULATOR_HOST'):
        from google.auth.credentials import AnonymousCredentials

        anon_credentials = AnonymousCredentials()
        storage_client = storage.Client(
            client_info=get_grpc_client_info(),
            client_options={"api_endpoint": os.getenv('STORAGE_EMULATOR_HOST')},
            credentials=anon_credentials)
    else:
        storage_client = storage.Client(client_info=get_grpc_client_info())
    bucket = storage_client.bucket(ignore_config['bucket'])
    resend_blob = bucket.blob(resend_file)
    if resend_blob.exists():
        resend_blob.reload()
        resend_period = ignore_config['period']
        resend_period_parsed = parsedatetime.Calendar(
            version=parsedatetime.VERSION_CONTEXT_STYLE).parse(
                resend_period, sourceTime=resend_blob.time_created)
        if len(resend_period_parsed) > 1:
            resend_earliest = datetime.fromtimestamp(
                mktime(resend_period_parsed[0]))
        else:
            resend_earliest = datetime.fromtimestamp(
                mktime(resend_period_parsed))

        if datetime.utcnow() >= resend_earliest:
            logger.info('Ignore period elapsed, reprocessing the message now.',
                        extra={
                            'resend_earliest': resend_earliest,
                            'blob_time_created': resend_blob.time_created
                        })
            resend_blob.upload_from_string('')
        else:
            logger.info(
                'Ignore period not elapsed, not reprocessing the message.',
                extra={
                    'resend_earliest': resend_earliest,
                    'blob_time_created': resend_blob.time_created
                })
            return False
    else:
        try:
            resend_blob.upload_from_string('', if_generation_match=0)
        except Exception as exc:
            # Handle TOCTOU condition
            if 'conditionNotMet' in str(exc):
                logger.warning(
                    'Message processing already in progress (message ignore key already exist).',
                    extra={'exception': exc})
                return False
            else:
                raise exc
    return True


def macro_helper(macro_func, *args, **kwargs):
    r = macro_func(*args, **kwargs)
    try:
        if r.strip().startswith('[') or r.strip().startswith('{'):
            e = eval(r)
            return e
        else:
            return r
    except SyntaxError:  # Probably a string, huh.
        return r


def process_message_pipeline(logger, config, data, event, context):
    template_variables = {
        'data': data,
        'event': event,
        'context': context,
    }
    if len(config['pipeline']) == 0:
        raise NoPipelineConfiguredException('Empty pipeline configured!')

    jinja_environment = get_jinja_environment()
    jinja_environment.globals = {
        **jinja_environment.globals,
        **template_variables
    }

    helper = BaseHelper(jinja_environment)

    if 'macros' in config:
        if not isinstance(config['macros'], list):
            raise MalformedMacrosException(
                '"macros" in configuration should be a list.')
        macros = {}
        for macro in config['macros']:
            macro_template = jinja_environment.from_string(
                macro['macro'].strip())
            macro_template.name = 'macro'
            macro_template.render()
            macro_module = macro_template.module

            for f in dir(macro_module):
                if not f.startswith("_") and callable(getattr(macro_module, f)):
                    macro_func = getattr(macro_module, f)
                    macros[f] = partial(macro_helper, macro_func)

        jinja_environment.globals.update(macros)

    if 'globals' in config:
        if not isinstance(config['globals'], dict):
            raise MalformedGlobalsException(
                '"globals" in configuration should be a dictionary.')

        template_globals = helper._jinja_expand_dict_all(
            config['globals'], 'globals')
        jinja_environment.globals = {
            **jinja_environment.globals,
            **template_globals
        }

    task_number = 1
    for task in config['pipeline']:
        if 'type' not in task or not task['type']:
            raise NoTypeInPipelineException('No type in pipeline task #%d: %s' %
                                            (task_number, str(task)))

        task_type, task_handler = task['type'].split('.', 2)
        if not task_type or not task_handler or task_type not in [
                'processor', 'output'
        ]:
            raise NoTypeInPipelineException(
                'Malformed type in pipeline task #%d: %s' %
                (task_number, str(task)))

        task_config = {}
        if 'config' in task:
            task_config = task['config']

        # Handle resend prevention mechanism
        if 'ignoreOn' in task:
            if not handle_ignore_on(logger, task['ignoreOn'], jinja_environment,
                                    template_variables):
                return

        # Handle stop processing mechanism
        if 'stopIf' in task:
            stopif_template = jinja_environment.from_string(task['stopIf'])
            stopif_template.name = 'stopif'
            stopif_contents = stopif_template.render()
            if stopif_contents.strip() != '':
                jinja_environment.globals['previous_run'] = False
                logger.info(
                    'Pipeline task #%d (%s) stop-if condition evaluated to true (non-empty), stopping processing.'
                    % (task_number, task['type']))
                helper._clean_tempdir()
                return

        # Handle conditional execution mechanism
        if 'runIf' in task:
            runif_template = jinja_environment.from_string(task['runIf'])
            runif_template.name = 'runif'
            runif_contents = runif_template.render()
            if runif_contents.strip() == '':
                jinja_environment.globals['previous_run'] = False
                logger.info(
                    'Pipeline task #%d (%s) run-if condition evaluated to false (empty), skipping task.'
                    % (task_number, task['type']))
                task_number += 1
                continue

        # Process task wide variables
        if 'variables' in task:
            for k, v in task['variables'].items():
                if isinstance(v, dict):
                    jinja_environment.globals[
                        k] = helper._jinja_expand_dict_all(v, 'variable')
                elif isinstance(v, list):
                    jinja_environment.globals[k] = helper._jinja_expand_list(
                        v, 'variable')
                elif isinstance(v, int):
                    jinja_environment.globals[k] = helper._jinja_expand_int(
                        v, 'variable')
                else:
                    jinja_environment.globals[k] = helper._jinja_expand_string(
                        v, 'variable')

        try:
            # Handle output variable expansion
            output_var = task['output'] if 'output' in task else None
            if output_var:
                if isinstance(output_var, str):
                    # Expand output variable if it's a Jinja expression
                    output_var_template = jinja_environment.from_string(
                        output_var)
                    output_var_template.name = 'output'
                    output_var = output_var_template.render()
                elif isinstance(output_var, dict):
                    new_output_var = {}
                    for k, v in output_var.items():
                        output_var_template = jinja_environment.from_string(v)
                        output_var_template.name = 'output'
                        new_output_var[k] = output_var_template.render()
                    output_var = new_output_var

            # Handle the actual work
            if task_type == 'processor':  # Handle processor
                processor = task_handler
                logger.debug('Pipeline task #%d (%s), running processor: %s' %
                             (task_number, task['type'], processor))
                mod = __import__('processors.%s' % processor)
                processor_module = getattr(mod, processor)
                processor_class = getattr(
                    processor_module, '%sProcessor' % processor.capitalize())

                processor_instance = processor_class(task_config,
                                                     jinja_environment, data,
                                                     event, context)
                if output_var:
                    processor_variables = processor_instance.process(
                        output_var=output_var)
                else:
                    processor_variables = processor_instance.process()
                template_variables.update(processor_variables)
                template_variables['previous_run'] = True
                jinja_environment.globals = {
                    **jinja_environment.globals,
                    **template_variables
                }
            elif task_type == 'output':  # Handle output
                output_type = task_handler
                logger.debug('Pipeline task #%d (%s), running output: %s' %
                             (task_number, task['type'], output_type))
                mod = __import__('output.%s' % output_type)
                output_module = getattr(mod, output_type)
                output_class = getattr(output_module,
                                       '%sOutput' % output_type.capitalize())
                output_instance = output_class(task_config, task_config,
                                               jinja_environment, data, event,
                                               context)
                output_instance.output()
                jinja_environment.globals['previous_run'] = True
        except Exception as exc:
            jinja_environment.globals['previous_run'] = False
            if 'canFail' not in task or not task['canFail']:

                # Global output if a task fails
                if 'onError' in config:
                    error_task = config['onError']
                    if 'type' not in error_task or not error_task['type']:
                        raise NoTypeInPipelineException(
                            'No type in pipeline onError task')

                    jinja_environment.globals['exception'] = str(exc)

                    error_task_type, error_task_handler = error_task[
                        'type'].split('.', 2)

                    error_task_config = {}
                    if 'config' in error_task:
                        error_task_config = error_task['config']

                    output_type = error_task_handler
                    logger.debug(
                        'Pipeline onError task (%s), running output: %s' %
                        (error_task['type'], output_type))
                    mod = __import__('output.%s' % output_type)
                    output_module = getattr(mod, output_type)
                    output_class = getattr(
                        output_module, '%sOutput' % output_type.capitalize())
                    output_instance = output_class(error_task_config,
                                                   error_task_config,
                                                   jinja_environment, data,
                                                   event, context)
                    output_instance.output()

                logger.error(
                    'Pipeline task #%d (%s) failed, stopping processing.' %
                    (task_number, task['type']),
                    extra={'exception': traceback.format_exc()})
                if 'canFail' in config and config['canFail']:
                    logger.warn(
                        'Pipeline failed, but it is allowed to fail. Message processed.'
                    )
                    helper._clean_tempdir()
                    return
                else:
                    helper._clean_tempdir()
                    raise exc
            else:
                logger.warning(
                    'Pipeline task #%d (%s) failed, but continuing...' %
                    (task_number, task['type']),
                    extra={'exception': traceback.format_exc()})

        task_number += 1
    helper._clean_tempdir()


def process_message(config, data, event, context):
    logger = logging.getLogger('pubsub2inbox')

    check_retry_period(config, context, logger)

    if 'pipeline' in config and isinstance(config['pipeline'], list):
        process_message_pipeline(logger, config, data, event, context)
    else:
        process_message_legacy(logger, config, data, event, context)


def decode_and_process(logger, config, event, context):
    if 'data' not in event:
        raise NoDataFieldException('No data field in Pub/Sub message!')

    logger.debug('Decoding Pub/Sub message...',
                 extra={
                     'event_id': context.event_id,
                     'timestamp': context.timestamp,
                     'hostname': socket.gethostname(),
                     'pid': os.getpid()
                 })
    if event['data'] != '':
        data = base64.b64decode(event['data']).decode('raw_unicode_escape')
    else:
        data = None

    logger.debug('Starting Pub/Sub message processing...',
                 extra={
                     'event_id': context.event_id,
                     'data': data,
                     'attributes': event['attributes']
                 })
    process_message(config, data, event, context)
    logger.debug('Pub/Sub message processing finished.',
                 extra={'event_id': context.event_id})


def process_pubsub(event, context, message_too_old_exception=False):
    """Function that is triggered by Pub/Sub incoming message.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    """
    global execution_count, configuration, logger
    execution_count += 1

    if not logger:
        logger = setup_logging()
    logger.debug('Received a Pub/Sub message.',
                 extra={
                     'event_id': context.event_id,
                     'timestamp': context.timestamp,
                     'hostname': socket.gethostname(),
                     'pid': os.getpid(),
                     'execution_count': execution_count
                 })
    socket.setdefaulttimeout(10)
    if not configuration:
        configuration = load_configuration(config_file_name)
    try:
        decode_and_process(logger, configuration, event, context)
    except TemplateError as exc:
        logger.error('Error while evaluating a Jinja2 template!',
                     extra={
                         'error_message': exc,
                         'error': str(exc),
                     })
        raise exc
    except MessageTooOldException as mtoe:
        if not message_too_old_exception:
            pass
        else:
            raise (mtoe)


def process_pubsub_v2(event, context, message_too_old_exception=False):
    """Function that is triggered by Pub/Sub incoming message for functions V2.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    """
    global logger

    if not logger:
        logger = setup_logging()

    new_context = Context(eventId=context.event_id,
                          timestamp=context.timestamp,
                          eventType=context.event_type,
                          resource=context.resource)
    if 'attributes' not in event:
        event['attributes'] = {}
    if 'data' not in event:
        event['data'] = ''
    process_pubsub(event, new_context)


class CloudRunServer:

    def on_get(self, req, res):
        try:
            import falcon

            res.content_type = falcon.MEDIA_TEXT
            res.status = falcon.HTTP_400
            res.text = 'Bad Request: expecting POST'
        except ImportError:
            logger.error(
                'Falcon is required for web server mode, run: pip install falcon'
            )

    def on_post(self, req, res):
        try:
            import falcon
            res.content_type = falcon.MEDIA_TEXT

            try:
                envelope = req.media
            except falcon.MediaNotFoundError:
                raise NoMessageReceivedException('No Pub/Sub message received')
            except falcon.MediaMalformedError:
                raise InvalidMessageFormatException('Invalid Pub/Sub JSON')

            if not isinstance(envelope, dict) or 'message' not in envelope:
                raise InvalidMessageFormatException(
                    'Invalid Pub/Sub message format')

            event = {
                'data':
                    envelope['message']['data'],
                'attributes':
                    envelope['message']['attributes']
                    if 'attributes' in envelope['message'] else {}
            }

            context = Context(eventId=envelope['message']['messageId'],
                              timestamp=envelope['message']['publishTime'])
            process_pubsub(event, context, message_too_old_exception=True)
            res.status = falcon.HTTP_200
            res.text = 'Message processed.'
        except (NoMessageReceivedException,
                InvalidMessageFormatException) as me:
            # Do not attempt to retry malformed messages
            logger.error('%s' % (me),
                         extra={'exception': traceback.format_exc()})
            res.status = falcon.HTTP_204
            res.text = 'Bad Request: %s' % (str(me))
        except MessageTooOldException as mtoe:
            res.status = falcon.HTTP_202
            res.text = 'Message ignored: %s' % (mtoe)
        except ImportError:
            logger.error(
                'Falcon is required for web server mode, run: pip install falcon'
            )
        except Exception as e:
            traceback.print_exc()
            res.status = falcon.HTTP_500
            res.text = 'Internal Server Error: %s' % (e)


def setup_logging():
    logger = logging.getLogger('pubsub2inbox')
    if os.getenv('LOG_LEVEL') and os.getenv('LOG_LEVEL') != '':
        logger.setLevel(int(os.getenv('LOG_LEVEL')))
    else:
        logger.setLevel(logging.INFO)
    json_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    json_handler.setFormatter(formatter)
    logger.addHandler(json_handler)
    return logger


def run_webserver(run_locally=False):
    global logger
    if not logger:
        logger = setup_logging()
    try:
        import falcon
        app = falcon.App()
        server = CloudRunServer()
        app.add_route('/', server)
        if run_locally:
            from waitress import serve
            port = 8080 if not os.getenv('PORT') or os.getenv(
                'PORT') == '' else int(os.getenv('PORT'))
            serve(app, listen='*:%d' % (port))
        return app
    except ImportError:
        logger.error(
            'Falcon and waitress is required for web server mode, run: pip install falcon waitress'
        )


app = None
if os.getenv('WEBSERVER') == '1':
    app = run_webserver()

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='Pub/Sub to Inbox, turn Pub/Sub messages into emails')
    arg_parser.add_argument('--config', type=str, help='Configuration file')
    arg_parser.add_argument(
        '--ignore-period',
        action='store_true',
        help='Ignore the message timestamp (for skipping retry period)')
    arg_parser.add_argument('--webserver',
                            action='store_true',
                            help='Run the function as a web server')
    arg_parser.add_argument('message',
                            type=str,
                            nargs='?',
                            help='JSON file containing the message(s)')
    arg_parser.add_argument('--set',
                            nargs='*',
                            type=lambda s: tuple(s.split('=', 2)),
                            help='Set a Jinja variable from command line')
    args = arg_parser.parse_args()
    if args.config:
        config_file_name = args.config
    if args.set:
        extra_vars = args.set
    if args.webserver or os.getenv('WEBSERVER') == '1':
        run_webserver(True)
    else:
        if not args.message:
            print(
                'Specify a file containing the message to process on the command line.'
            )
        with open(args.message) as f:
            contents = f.read()
            messages = json.loads(contents)
            for message in messages:
                event = {
                    'data':
                        message['message']['data']
                        if 'data' in message['message'] else '',
                    'attributes':
                        message['message']['attributes']
                        if 'attributes' in message['message'] else {}
                }
                context = Context(eventId=message['message']['messageId'],
                                  timestamp=message['message']['publishTime'])
                if args.ignore_period:
                    context.timestamp = datetime.utcnow().strftime(
                        '%Y-%m-%dT%H:%M:%S.%fZ')
                process_pubsub(event, context)
