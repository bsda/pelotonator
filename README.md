# Pelotonator - Peloton delivery re-scheduler

Did you just order a Peloton but the delivery time is far away?

Instead of manually checking for new slots, you can add this script to a cron job to do it for you



## Requirements
 - python3

You'll also need the following

- The order id from the re-schedule URL you received from Peloton. 
  This bit: **2e5f46f48d8444a9ec70196a9e0da0d10** From an url like this: https://www.onepeloton.com/delivery/2e5f46f48d8444a9ec70196a9e0da0d10/reschedule
- (Optional) A Slack Incoming Webhook URL to receive notifications when a new slot is found (set one up [here](https://echo.slack.com/apps/A0F7XDUAZ-incoming-webhooks); search for yourself in the channel dropdown)


## Installation 
`pip3 install -r requirements.txt`

## Running

Copy config.py.example to config.py and update the order_id and slack_webhook_url values with your ones.

```
python3 pelotonator.py

Checking for delivery slots...
Found an earlier slot
Current slot: 2021-03-13 08:00:00+00:00
Next slot available: 2021-03-10 10:00:00+00:00
Trying to pick the new slot...
Yay, new slot set
New delivery times set to between 2021-03-10 10:00:00+00:00 and 2021-03-10 12:00:00+00:00

```

### Cron job

I have no idea if there is monitoring or throttling on their end, I wouldn't run this script very often anyway. 

**I'm not responsible for any actions Peloton takes against you or your order if you abuse their api**

<br>

Running it every 2 hours in cron:

`0 */2 * * * /path/to/python3 /path/to/pelotonator.py`



### Why?

Why not?

