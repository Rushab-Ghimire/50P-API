from subscription.payment_utils import PaymentUtils

class SubscriptionHelper:

    def assign_default_subscription_for_new_user(user):
        print("called assign_default_subscription_for_new_user")
        return
        plan_id = "Trial-USD-Monthly"
        customer = {
            "cf_ad_user_id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        cb_customer = PaymentUtils().create_customer(customer)

        subscription = {
            "billing_cycles": 1,
            "subscription_items": [{"item_price_id": plan_id}]
        }
        return PaymentUtils().create_subscription(cb_customer.customer.id, subscription)

    def assing_referee_subscription_for_new_user(user):
        return
        plan_id = "Premium-USD-Monthly"
        customer = {
            "cf_ad_user_id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        cb_customer = PaymentUtils().create_customer(customer)

        subscription = {
            "subscription_items": [{"item_price_id": plan_id}],
            "discounts":[{
                "apply_on": "invoice_amount",
                "duration_type": "one_time",
                "percentage": 100,
                "operation_type": "add"
            }]
        }
        return PaymentUtils().create_subscription(cb_customer.customer.id, subscription)

    def assign_referrer_subscription(user):
        return
        plan_id = "Premium-USD-Monthly"

        subscription = {
            "billing_cycles": 3,
            "subscription_items": [{"item_price_id": plan_id}],
            "discounts":[{
                "apply_on": "invoice_amount",
                "duration_type": "limited_period",
                "period": 3,
                "period_unit": "month",
                "percentage": 100,
                "operation_type": "add"
            }]
        }

        chargebee_user = user.get_chargebee_customer()
        if chargebee_user:
            if chargebee_user.subscription:
                return PaymentUtils().update_subscription(chargebee_user.subscription.id, subscription)
            cb_customer_id = chargebee_user.customer_id
        else:
            customer = {
                "cf_ad_user_id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
            cb_customer = PaymentUtils().create_customer(customer)
            cb_customer_id = cb_customer.customer.id

        return PaymentUtils().create_subscription(cb_customer_id, subscription)

