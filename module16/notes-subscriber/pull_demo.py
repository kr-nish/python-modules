from google.cloud import pubsub_v1
import os

os.environ['PUBSUB_EMULATOR_HOST'] = ''
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path('edurekali-1620623900283','pull-sub')

def callback(message):
    print(f"Pull recived: {message.data.decode('utf-8')}")
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print("Pull subscriber listening... ")

try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()