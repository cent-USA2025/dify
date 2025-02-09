# -*- coding:utf-8 -*-
import logging

import services
from controllers.console import api
from controllers.console.app.error import (AppUnavailableError, AudioTooLargeError, CompletionRequestError,
                                           NoAudioUploadedError, ProviderModelCurrentlyNotSupportError,
                                           ProviderNotInitializeError, ProviderNotSupportSpeechToTextError,
                                           ProviderQuotaExceededError, UnsupportedAudioTypeError)
from controllers.console.explore.wraps import InstalledAppResource
from core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, QuotaExceededError
from core.model_runtime.errors.invoke import InvokeError
from flask import request
from models.model import AppModelConfig
from services.audio_service import AudioService
from services.errors.audio import (AudioTooLargeServiceError, NoAudioUploadedServiceError,
                                   ProviderNotSupportSpeechToTextServiceError, UnsupportedAudioTypeServiceError)
from werkzeug.exceptions import InternalServerError


class ChatAudioApi(InstalledAppResource):
    def post(self, installed_app):
        app_model = installed_app.app
        app_model_config: AppModelConfig = app_model.app_model_config

        if not app_model_config.speech_to_text_dict['enabled']:
            raise AppUnavailableError()

        file = request.files['file']

        try:
            response = AudioService.transcript_asr(
                tenant_id=app_model.tenant_id,
                file=file,
            )

            return response
        except services.errors.app_model_config.AppModelConfigBrokenError:
            logging.exception("App model config broken.")
            raise AppUnavailableError()
        except NoAudioUploadedServiceError:
            raise NoAudioUploadedError()
        except AudioTooLargeServiceError as e:
            raise AudioTooLargeError(str(e))
        except UnsupportedAudioTypeServiceError:
            raise UnsupportedAudioTypeError()
        except ProviderNotSupportSpeechToTextServiceError:
            raise ProviderNotSupportSpeechToTextError()
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except InvokeError as e:
            raise CompletionRequestError(e.description)
        except ValueError as e:
            raise e
        except Exception as e:
            logging.exception("internal server error.")
            raise InternalServerError()


class ChatTextApi(InstalledAppResource):
    def post(self, installed_app):
        app_model = installed_app.app
        app_model_config: AppModelConfig = app_model.app_model_config

        if not app_model_config.text_to_speech_dict['enabled']:
            raise AppUnavailableError()

        try:
            response = AudioService.transcript_tts(
                tenant_id=app_model.tenant_id,
                text=request.form['text'],
                streaming=False
            )
            return {'data': response.data.decode('latin1')}
        except services.errors.app_model_config.AppModelConfigBrokenError:
            logging.exception("App model config broken.")
            raise AppUnavailableError()
        except NoAudioUploadedServiceError:
            raise NoAudioUploadedError()
        except AudioTooLargeServiceError as e:
            raise AudioTooLargeError(str(e))
        except UnsupportedAudioTypeServiceError:
            raise UnsupportedAudioTypeError()
        except ProviderNotSupportSpeechToTextServiceError:
            raise ProviderNotSupportSpeechToTextError()
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except InvokeError as e:
            raise CompletionRequestError(e.description)
        except ValueError as e:
            raise e
        except Exception as e:
            logging.exception("internal server error.")
            raise InternalServerError()


api.add_resource(ChatAudioApi, '/installed-apps/<uuid:installed_app_id>/audio-to-text', endpoint='installed_app_audio')
api.add_resource(ChatTextApi, '/installed-apps/<uuid:installed_app_id>/text-to-audio', endpoint='installed_app_text')
