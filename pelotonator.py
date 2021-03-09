#!/usr/bin/env python3

import requests
from dateutil.parser import parse
from config import slack_webhook_url, order_id
import logging

logging.basicConfig(
    level='INFO', format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger()

url = 'https://graph.prod.k8s.onepeloton.com/graphql'
headers = {'content-type': 'application/json'}


def slack(message):
    payload = {'text': f'{message} :bike:'}
    requests.post(slack_webhook_url, json=payload, headers={'Content-Type': 'application/json'})


def get_delivery_slots(order_id):
    query = """
    query OrderDelivery($id: ID!, $isReschedule: Boolean = false) {
      order(id: $id) {
        canSetDeliveryPreference
        canReschedule
        canSelectTimeSlot
        deliveryPreference {
          date
          start
          end
          __typename
        }
        availableDeliveries(limit: 100, isReschedule: $isReschedule) {
          id
          date
          start
          end
          __typename
        }
        __typename
      }
      postPurchaseFlow(id: $id) {
        permission
        __typename
      }
    }
    """
    payload = {"operationName": "OrderDelivery",
               "variables": {
                   "isReschedule": True,
                   "id": order_id
               },
               "query": query
               }

    logger.info('Checking for delivery slots...')
    try:
        res = requests.post(url, json=payload, headers=headers)
        data = res.json()
    except requests.exceptions.RequestException as e:
        logger.info(f'Error getting delivery slots: {e}')
        raise
    else:
        current_date = parse(data['data']['order']['deliveryPreference']['start'])
        available = data['data']['order']['availableDeliveries']
        next_date = parse(available[0]['start'])

    if next_date < current_date:
        logger.info('Found an earlier slot')
        logger.info(f'Current slot: {str(current_date)}')
        logger.info(f'Next slot available: {str(next_date)}')
        return available[0]['id']

    logger.info('No luck, earliest slot is later than current slot')
    logger.info(f'Current slot: {str(current_date)}')
    logger.info(f'Next slot available: {str(next_date)}')
    logger.info("Not updating")
    return False


def set_delivery_slot(delivery_id, order_id):
    query = """
    mutation SetDeliveryPreference($orderId: ID!, $deliveryId: ID!, $isReschedule: Boolean = false) {
  orderSetDeliveryPreference(orderId: $orderId, deliveryId: $deliveryId, isReschedule: $isReschedule) {
    deliveryPreference {
      date
      start
      end
      __typename
    }
    __typename
  }
}
    """
    payload = {"operationName": "SetDeliveryPreference",
               "variables": {
                   "isReschedule": True,
                   "deliveryId": delivery_id,
                   "orderId": order_id
               },
               "query": query
               }

    try:
        res = requests.post(url, json=payload, headers=headers)
        data = res.json()
    except requests.exceptions.RequestException as e:
        logger.info(f'Error setting new slot: {e}')
        raise
    else:
        new_slot = {
            'start': parse(data['data']['orderSetDeliveryPreference']['deliveryPreference']['start']),
            'end': parse(data['data']['orderSetDeliveryPreference']['deliveryPreference']['end'])
        }
        return new_slot


def main():
    logger.info(f'Starting Pelotonator')
    new_delivery_id = get_delivery_slots(order_id)
    if new_delivery_id:
        logger.info('Trying to pick the new slot...')
        new_slot = set_delivery_slot(new_delivery_id, order_id)
        if slack_webhook_url:
            slack(f'Yo, you got a new delivery date: {new_slot["start"]}')
        logger.info('Yay, new slot set')
        logger.info(f'New delivery times set to between {new_slot["start"]} and {new_slot["end"]}')


if __name__ == "__main__":
    main()