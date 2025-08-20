
from decimal import Decimal

class TaskSuite:

    def construct_worker_payload(self, worker: dict, nonce: dict) -> tuple:
        ctx = {}  # Simulate context.Background()

        if worker['InferenceEntrypoint'] is None and worker['ForecastEntrypoint'] is None:
            print("Error: Worker lacks valid Inference or Forecast entrypoints")
            return False, None

        worker_response = {
            'WorkerConfig': worker
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
                    return False, err
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

    def construct_payload(self, worker_response: dict, height: int) -> tuple:
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

    def secure_worker_payload(self, payload: dict) -> tuple:
        proto_bytes = b""  # Simulate creating a byte slice

        try:
            proto_bytes = self.simulate_marshal(proto_bytes, payload, True)
            if proto_bytes is None:
                print("Error during marshaling")
                return {}, None

            sig, pk, err = self.mock_sign(self.node['chain']['account']['name'], proto_bytes)
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

    def convert_to_dec(self, value: str) -> tuple:
        try:
            dec_value = Decimal(value)
            return dec_value, None
        except Exception as ex:
            print(f"Error converting {value} to decimal: {str(ex)}")
            return None, ex

    def log_scale(self, value: Decimal) -> Decimal:
        # Placeholder for log scaling
        return value

    def simulate_marshal(self, proto_bytes: bytes, payload: dict, flag: bool) -> bytes:
        # Placeholder for marshaling simulation
        return proto_bytes

    def mock_sign(self, account_name: str, data: bytes) -> tuple:
        # Placeholder for signing logic
        return b"signature", b"public_key", None

    def send_with_retry(self, ctx: dict, req: dict, message: str) -> tuple:
        # Placeholder for sending with retry logic
        return None, None
