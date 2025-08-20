from decimal import Decimal
import math

class TaskSuite:
    def __init__(self):
        self.node = {
            'wallet': {
                'address': 'test_address',
                'submit_tx': True,
                'sign': self.mock_sign
            },
            'chain': {
                'account': {
                    'name': 'test_account'
                }
            }
        }

    def construct_worker_payload(self, worker, nonce):
        ctx = {}  # Simulate context.Background()

        if worker['InferenceEntrypoint'] is None and worker['ForecastEntrypoint'] is None:
            print("Error: Worker lacks valid Inference or Forecast entrypoints")
            return False, None

        worker_response = {
            'WorkerConfig': worker,
            'TopicId': worker.get('TopicId', '')
        }

        try:
            if worker['InferenceEntrypoint'] is not None:
                inference, err = worker['InferenceEntrypoint'].compute(worker, nonce['block_height'])
                if err is not None:
                    print(f"Error computing inference for {worker['InferenceEntrypoint'].name()}")
                    return False, err
                worker_response['InfererValue'] = inference

            if worker['ForecastEntrypoint'] is not None:
                forecasts = worker['ForecastEntrypoint'].forecast(worker, nonce['block_height'])
                if forecasts is None:
                    print(f"Error computing forecast for {worker['ForecastEntrypoint'].name()}")
                    return False, "Forecast error"
                worker_response['ForecasterValues'] = forecasts

            worker_payload, err = self.construct_payload(worker_response, nonce['block_height'])
            if err is not None:
                print("Error constructing worker payload")
                return False, err

            worker_bundle, err = self.secure_worker_payload(worker_payload)
            if err is not None:
                print("Error signing worker payload")
                return False, err

            worker_bundle['Nonce'] = nonce
            worker_bundle['TopicId'] = worker['TopicId']

            req = {
                'Sender': self.node['wallet']['address'],
                'WorkerDataBundle': worker_bundle
            }
            print(f"Sending worker payload with request {req} to chain")

            if self.node['wallet']['submit_tx']:
                _, err = self.send_with_retry(ctx, req, "Transmit Worker Data to chain")
                if err is not None:
                    print("Error transmitting Worker Data to chain")
                    return False, err
            else:
                print(f"Skipping chain transmission for TopicId={worker['TopicId']} due to disabled submit_tx flag")

        except Exception as ex:
            print(f"Exception occurred: {str(ex)}")
            return False, ex

        return True, None

    def construct_payload(self, worker_response, height):
        forecasts_bundle = {}
        
        try:
            if worker_response.get('InfererValue', "") != "":
                inferer_val, err = self.convert_to_dec(worker_response['InfererValue'])
                if err is not None:
                    print("Error converting inferer value")
                    return {}, err

                inference = {
                    'TopicId': worker_response['TopicId'],
                    'Inferer': self.node['wallet']['address'],
                    'Value': inferer_val,
                    'BlockHeight': height
                }
                forecasts_bundle['Inference'] = inference

            if len(worker_response.get('ForecasterValues', [])) > 0:
                elements = []
                for val in worker_response['ForecasterValues']:
                    val_dec, err = self.convert_to_dec(val['value'])
                    if err is not None:
                        print("Error converting forecast value to decimal")
                        return {}, err
                    if not worker_response.get('AllowsNegativeValue', False):
                        val_dec = self.log_scale(val_dec)

                    elements.append({
                        'Inferer': val['worker'],
                        'Value': val_dec
                    })

                forecast_values = {
                    'TopicId': worker_response['TopicId'],
                    'BlockHeight': height,
                    'Forecaster': self.node['wallet']['address'],
                    'ForecastElements': elements
                }
                forecasts_bundle['Forecast'] = forecast_values
            
        except Exception as ex:
            print(f"Exception occurred during payload construction: {str(ex)}")
            return {}, ex

        return forecasts_bundle, None

    def secure_worker_payload(self, payload):
        proto_bytes = b""  # Simulate creating a byte slice

        try:
            proto_bytes = self.simulate_marshal(proto_bytes, payload, True)
            if proto_bytes is None:
                print("Error during marshaling")
                return {}, None

            sig, pk, err = self.node['wallet']['sign'](self.node['chain']['account']['name'], proto_bytes)
            pk_str = pk.hex()
            if err is not None:
                print("Error signing the message")
                return {}, err

            worker_bundle = {
                'Worker': self.node['wallet']['address'],
                'InferenceForeBundles': payload,
                'InferencesBundleSignature': sig,
                'Pubkey': pk_str
            }
        except Exception as ex:
            print(f"Exception occurred during worker payload security: {str(ex)}")
            return {}, ex

        return worker_bundle, None

    def convert_to_dec(self, value):
        try:
            return Decimal(value), None
        except Exception as e:
            return None, str(e)

    def log_scale(self, value):
        return Decimal(math.log(float(value)))

    def simulate_marshal(self, proto_bytes, payload, flag):
        return b'marshaled_data'

    def mock_sign(self, account_name, data):
        return 'signature', b'public_key', None

    def send_with_retry(self, ctx, req, message):
        return None, None