import json

response_bought = json.loads("""
{
  "object": {
    "id": "in_1QDoXVGjSxKJrDncKznHAJcV",
    "object": "invoice",
    "account_country": "NL",
    "account_name": "SECRAG",
    "account_tax_ids": null,
    "amount_due": 1000,
    "amount_paid": 1000,
    "amount_remaining": 0,
    "amount_shipping": 0,
    "application": null,
    "application_fee_amount": null,
    "attempt_count": 1,
    "attempted": true,
    "auto_advance": false,
    "automatic_tax": {
      "enabled": false,
      "liability": null,
      "status": null
    },
    "automatically_finalizes_at": null,
    "billing_reason": "subscription_create",
    "charge": "py_3QDoXVGjSxKJrDnc0kYIQH4N",
    "collection_method": "charge_automatically",
    "created": 1729866657,
    "currency": "eur",
    "custom_fields": null,
    "customer": "cus_R60YYlyoaXunXU",
    "customer_address": null,
    "customer_email": "paul.bezko@hotmail.com",
    "customer_name": "Paul Bezkorovainijs",
    "customer_phone": null,
    "customer_shipping": null,
    "customer_tax_exempt": "none",
    "customer_tax_ids": [
    ],
    "default_payment_method": null,
    "default_source": null,
    "default_tax_rates": [
    ],
    "description": null,
    "discount": null,
    "discounts": [
    ],
    "due_date": null,
    "effective_at": 1729866657,
    "ending_balance": 0,
    "footer": null,
    "from_invoice": null,
    "hosted_invoice_url": "https://invoice.stripe.com/i/acct_1PtWwQGjSxKJrDnc/test_YWNjdF8xUHRXd1FHalN4S0pyRG5jLF9SNjBZTjF2TzB0WE15UGJTWE1qUm10bGNNZlZ2NWtQLDEyMDQwNzUwOQ0200yDbPznPh?s=ap",
    "invoice_pdf": "https://pay.stripe.com/invoice/acct_1PtWwQGjSxKJrDnc/test_YWNjdF8xUHRXd1FHalN4S0pyRG5jLF9SNjBZTjF2TzB0WE15UGJTWE1qUm10bGNNZlZ2NWtQLDEyMDQwNzUwOQ0200yDbPznPh/pdf?s=ap",
    "issuer": {
      "type": "self"
    },
    "last_finalization_error": null,
    "latest_revision": null,
    "lines": {
      "object": "list",
      "data": [
        {
          "id": "il_1QDoXVGjSxKJrDnctBFeIt8P",
          "object": "line_item",
          "amount": 1000,
          "amount_excluding_tax": 1000,
          "currency": "eur",
          "description": "1 × SECRag Basic (at €10.00 / month)",
          "discount_amounts": [
          ],
          "discountable": true,
          "discounts": [
          ],
          "invoice": "in_1QDoXVGjSxKJrDncKznHAJcV",
          "livemode": false,
          "metadata": {
          },
          "period": {
            "end": 1732545057,
            "start": 1729866657
          },
          "plan": {
            "id": "price_1PtWxIGjSxKJrDncAmBA32TK",
            "object": "plan",
            "active": true,
            "aggregate_usage": null,
            "amount": 1000,
            "amount_decimal": "1000",
            "billing_scheme": "per_unit",
            "created": 1725032504,
            "currency": "eur",
            "interval": "month",
            "interval_count": 1,
            "livemode": false,
            "metadata": {
            },
            "meter": null,
            "nickname": null,
            "product": "prod_Ql33AItOLX5dZo",
            "tiers_mode": null,
            "transform_usage": null,
            "trial_period_days": null,
            "usage_type": "licensed"
          },
          "pretax_credit_amounts": [
          ],
          "price": {
            "id": "price_1PtWxIGjSxKJrDncAmBA32TK",
            "object": "price",
            "active": true,
            "billing_scheme": "per_unit",
            "created": 1725032504,
            "currency": "eur",
            "custom_unit_amount": null,
            "livemode": false,
            "lookup_key": null,
            "metadata": {
            },
            "nickname": null,
            "product": "prod_Ql33AItOLX5dZo",
            "recurring": {
              "aggregate_usage": null,
              "interval": "month",
              "interval_count": 1,
              "meter": null,
              "trial_period_days": null,
              "usage_type": "licensed"
            },
            "tax_behavior": "unspecified",
            "tiers_mode": null,
            "transform_quantity": null,
            "type": "recurring",
            "unit_amount": 1000,
            "unit_amount_decimal": "1000"
          },
          "proration": false,
          "proration_details": {
            "credited_items": null
          },
          "quantity": 1,
          "subscription": "sub_1QDoXVGjSxKJrDncYU0vmavf",
          "subscription_item": "si_R60YaxSr3oVzSg",
          "tax_amounts": [
          ],
          "tax_rates": [
          ],
          "type": "subscription",
          "unit_amount_excluding_tax": "1000"
        }
      ],
      "has_more": false,
      "total_count": 1,
      "url": "/v1/invoices/in_1QDoXVGjSxKJrDncKznHAJcV/lines"
    },
    "livemode": false,
    "metadata": {
    },
    "next_payment_attempt": null,
    "number": "B65BC86E-0082",
    "on_behalf_of": null,
    "paid": true,
    "paid_out_of_band": false,
    "payment_intent": "pi_3QDoXVGjSxKJrDnc0yZtSwjw",
    "payment_settings": {
      "default_mandate": null,
      "payment_method_options": {
        "acss_debit": null,
        "bancontact": null,
        "card": {
          "request_three_d_secure": "automatic"
        },
        "customer_balance": null,
        "konbini": null,
        "sepa_debit": null,
        "us_bank_account": null
      },
      "payment_method_types": null
    },
    "period_end": 1729866657,
    "period_start": 1729866657,
    "post_payment_credit_notes_amount": 0,
    "pre_payment_credit_notes_amount": 0,
    "quote": null,
    "receipt_number": null,
    "rendering": null,
    "shipping_cost": null,
    "shipping_details": null,
    "starting_balance": 0,
    "statement_descriptor": null,
    "status": "paid",
    "status_transitions": {
      "finalized_at": 1729866657,
      "marked_uncollectible_at": null,
      "paid_at": 1729866708,
      "voided_at": null
    },
    "subscription": "sub_1QDoXVGjSxKJrDncYU0vmavf",
    "subscription_details": {
      "metadata": {
      }
    },
    "subtotal": 1000,
    "subtotal_excluding_tax": 1000,
    "tax": null,
    "test_clock": null,
    "total": 1000,
    "total_discount_amounts": [
    ],
    "total_excluding_tax": 1000,
    "total_pretax_credit_amounts": [
    ],
    "total_tax_amounts": [
    ],
    "transfer_data": null,
    "webhooks_delivered_at": 1729866660
  }
}
"""
)

response_switched = json.loads("""
{
  "object": {
    "id": "in_1QDoZIGjSxKJrDnc6m6UIHrS",
    "object": "invoice",
    "account_country": "NL",
    "account_name": "SECRAG",
    "account_tax_ids": null,
    "amount_due": 1000,
    "amount_paid": 1000,
    "amount_remaining": 0,
    "amount_shipping": 0,
    "application": null,
    "application_fee_amount": null,
    "attempt_count": 1,
    "attempted": true,
    "auto_advance": false,
    "automatic_tax": {
      "enabled": false,
      "liability": null,
      "status": null
    },
    "automatically_finalizes_at": null,
    "billing_reason": "subscription_update",
    "charge": "py_3QDoZJGjSxKJrDnc03rQWjkm",
    "collection_method": "charge_automatically",
    "created": 1729866768,
    "currency": "eur",
    "custom_fields": null,
    "customer": "cus_R60YYlyoaXunXU",
    "customer_address": null,
    "customer_email": "paul.bezko@hotmail.com",
    "customer_name": "Paul Bezkorovainijs",
    "customer_phone": null,
    "customer_shipping": null,
    "customer_tax_exempt": "none",
    "customer_tax_ids": [
    ],
    "default_payment_method": null,
    "default_source": null,
    "default_tax_rates": [
    ],
    "description": null,
    "discount": null,
    "discounts": [
    ],
    "due_date": null,
    "effective_at": 1729866768,
    "ending_balance": 0,
    "footer": null,
    "from_invoice": null,
    "hosted_invoice_url": "https://invoice.stripe.com/i/acct_1PtWwQGjSxKJrDnc/test_YWNjdF8xUHRXd1FHalN4S0pyRG5jLF9SNjBhY0dCSkV5NUR2dkh2SnowM0dObnEzTGxzWUFCLDEyMDQwNzY5NA0200JWM1nxOi?s=ap",
    "invoice_pdf": "https://pay.stripe.com/invoice/acct_1PtWwQGjSxKJrDnc/test_YWNjdF8xUHRXd1FHalN4S0pyRG5jLF9SNjBhY0dCSkV5NUR2dkh2SnowM0dObnEzTGxzWUFCLDEyMDQwNzY5NA0200JWM1nxOi/pdf?s=ap",
    "issuer": {
      "type": "self"
    },
    "last_finalization_error": null,
    "latest_revision": null,
    "lines": {
      "object": "list",
      "data": [
        {
          "id": "il_1QDoZIGjSxKJrDncO64Rfqlg",
          "object": "line_item",
          "amount": -1000,
          "amount_excluding_tax": -1000,
          "currency": "eur",
          "description": "Unused time on SECRag Basic after 25 Oct 2024",
          "discount_amounts": [
          ],
          "discountable": false,
          "discounts": [
          ],
          "invoice": "in_1QDoZIGjSxKJrDnc6m6UIHrS",
          "invoice_item": "ii_1QDoZIGjSxKJrDncgb2MB8rj",
          "livemode": false,
          "metadata": {
          },
          "period": {
            "end": 1732545057,
            "start": 1729866729
          },
          "plan": {
            "id": "price_1PtWxIGjSxKJrDncAmBA32TK",
            "object": "plan",
            "active": true,
            "aggregate_usage": null,
            "amount": 1000,
            "amount_decimal": "1000",
            "billing_scheme": "per_unit",
            "created": 1725032504,
            "currency": "eur",
            "interval": "month",
            "interval_count": 1,
            "livemode": false,
            "metadata": {
            },
            "meter": null,
            "nickname": null,
            "product": "prod_Ql33AItOLX5dZo",
            "tiers_mode": null,
            "transform_usage": null,
            "trial_period_days": null,
            "usage_type": "licensed"
          },
          "pretax_credit_amounts": [
          ],
          "price": {
            "id": "price_1PtWxIGjSxKJrDncAmBA32TK",
            "object": "price",
            "active": true,
            "billing_scheme": "per_unit",
            "created": 1725032504,
            "currency": "eur",
            "custom_unit_amount": null,
            "livemode": false,
            "lookup_key": null,
            "metadata": {
            },
            "nickname": null,
            "product": "prod_Ql33AItOLX5dZo",
            "recurring": {
              "aggregate_usage": null,
              "interval": "month",
              "interval_count": 1,
              "meter": null,
              "trial_period_days": null,
              "usage_type": "licensed"
            },
            "tax_behavior": "unspecified",
            "tiers_mode": null,
            "transform_quantity": null,
            "type": "recurring",
            "unit_amount": 1000,
            "unit_amount_decimal": "1000"
          },
          "proration": true,
          "proration_details": {
            "credited_items": {
              "invoice": "in_1QDoXVGjSxKJrDncKznHAJcV",
              "invoice_line_items": [
                "il_1QDoXVGjSxKJrDnctBFeIt8P"
              ]
            }
          },
          "quantity": 1,
          "subscription": "sub_1QDoXVGjSxKJrDncYU0vmavf",
          "subscription_item": "si_R60YaxSr3oVzSg",
          "tax_amounts": [
          ],
          "tax_rates": [
          ],
          "type": "invoiceitem",
          "unit_amount_excluding_tax": "-1000"
        },
        {
          "id": "il_1QDoZJGjSxKJrDncGc70N4Xm",
          "object": "line_item",
          "amount": 2000,
          "amount_excluding_tax": 2000,
          "currency": "eur",
          "description": "Remaining time on SECRag Premium after 25 Oct 2024",
          "discount_amounts": [
          ],
          "discountable": false,
          "discounts": [
          ],
          "invoice": "in_1QDoZIGjSxKJrDnc6m6UIHrS",
          "invoice_item": "ii_1QDoZIGjSxKJrDncPrRhS0K1",
          "livemode": false,
          "metadata": {
          },
          "period": {
            "end": 1732545057,
            "start": 1729866729
          },
          "plan": {
            "id": "price_1PtWxYGjSxKJrDncZzwjeHQs",
            "object": "plan",
            "active": true,
            "aggregate_usage": null,
            "amount": 2000,
            "amount_decimal": "2000",
            "billing_scheme": "per_unit",
            "created": 1725032520,
            "currency": "eur",
            "interval": "month",
            "interval_count": 1,
            "livemode": false,
            "metadata": {
            },
            "meter": null,
            "nickname": null,
            "product": "prod_Ql33v0kldhhoqs",
            "tiers_mode": null,
            "transform_usage": null,
            "trial_period_days": null,
            "usage_type": "licensed"
          },
          "pretax_credit_amounts": [
          ],
          "price": {
            "id": "price_1PtWxYGjSxKJrDncZzwjeHQs",
            "object": "price",
            "active": true,
            "billing_scheme": "per_unit",
            "created": 1725032520,
            "currency": "eur",
            "custom_unit_amount": null,
            "livemode": false,
            "lookup_key": null,
            "metadata": {
            },
            "nickname": null,
            "product": "prod_Ql33v0kldhhoqs",
            "recurring": {
              "aggregate_usage": null,
              "interval": "month",
              "interval_count": 1,
              "meter": null,
              "trial_period_days": null,
              "usage_type": "licensed"
            },
            "tax_behavior": "unspecified",
            "tiers_mode": null,
            "transform_quantity": null,
            "type": "recurring",
            "unit_amount": 2000,
            "unit_amount_decimal": "2000"
          },
          "proration": true,
          "proration_details": {
            "credited_items": null
          },
          "quantity": 1,
          "subscription": "sub_1QDoXVGjSxKJrDncYU0vmavf",
          "subscription_item": "si_R60YaxSr3oVzSg",
          "tax_amounts": [
          ],
          "tax_rates": [
          ],
          "type": "invoiceitem",
          "unit_amount_excluding_tax": "2000"
        }
      ],
      "has_more": false,
      "total_count": 2,
      "url": "/v1/invoices/in_1QDoZIGjSxKJrDnc6m6UIHrS/lines"
    },
    "livemode": false,
    "metadata": {
    },
    "next_payment_attempt": null,
    "number": "B65BC86E-0083",
    "on_behalf_of": null,
    "paid": true,
    "paid_out_of_band": false,
    "payment_intent": "pi_3QDoZJGjSxKJrDnc0mMNaBMo",
    "payment_settings": {
      "default_mandate": null,
      "payment_method_options": {
        "acss_debit": null,
        "bancontact": null,
        "card": {
          "request_three_d_secure": "automatic"
        },
        "customer_balance": null,
        "konbini": null,
        "sepa_debit": null,
        "us_bank_account": null
      },
      "payment_method_types": null
    },
    "period_end": 1729866768,
    "period_start": 1729866657,
    "post_payment_credit_notes_amount": 0,
    "pre_payment_credit_notes_amount": 0,
    "quote": null,
    "receipt_number": null,
    "rendering": null,
    "shipping_cost": null,
    "shipping_details": null,
    "starting_balance": 0,
    "statement_descriptor": null,
    "status": "paid",
    "status_transitions": {
      "finalized_at": 1729866768,
      "marked_uncollectible_at": null,
      "paid_at": 1729866893,
      "voided_at": null
    },
    "subscription": "sub_1QDoXVGjSxKJrDncYU0vmavf",
    "subscription_details": {
      "metadata": {
      }
    },
    "subtotal": 1000,
    "subtotal_excluding_tax": 1000,
    "tax": null,
    "test_clock": null,
    "total": 1000,
    "total_discount_amounts": [
    ],
    "total_excluding_tax": 1000,
    "total_pretax_credit_amounts": [
    ],
    "total_tax_amounts": [
    ],
    "transfer_data": null,
    "webhooks_delivered_at": 1729866771
  }
}
"""
)

response_switched_again = json.loads("""
{
  "object": {
    "id": "in_1QDoa5GjSxKJrDncjsfYN40T",
    "object": "invoice",
    "account_country": "NL",
    "account_name": "SECRAG",
    "account_tax_ids": null,
    "amount_due": 8000,
    "amount_paid": 8000,
    "amount_remaining": 0,
    "amount_shipping": 0,
    "application": null,
    "application_fee_amount": null,
    "attempt_count": 1,
    "attempted": true,
    "auto_advance": false,
    "automatic_tax": {
      "enabled": false,
      "liability": null,
      "status": null
    },
    "automatically_finalizes_at": null,
    "billing_reason": "subscription_update",
    "charge": "py_3QDoa6GjSxKJrDnc0ISD7kd9",
    "collection_method": "charge_automatically",
    "created": 1729866817,
    "currency": "eur",
    "custom_fields": null,
    "customer": "cus_R60YYlyoaXunXU",
    "customer_address": null,
    "customer_email": "paul.bezko@hotmail.com",
    "customer_name": "Paul Bezkorovainijs",
    "customer_phone": null,
    "customer_shipping": null,
    "customer_tax_exempt": "none",
    "customer_tax_ids": [
    ],
    "default_payment_method": null,
    "default_source": null,
    "default_tax_rates": [
    ],
    "description": null,
    "discount": null,
    "discounts": [
    ],
    "due_date": null,
    "effective_at": 1729866817,
    "ending_balance": 0,
    "footer": null,
    "from_invoice": null,
    "hosted_invoice_url": "https://invoice.stripe.com/i/acct_1PtWwQGjSxKJrDnc/test_YWNjdF8xUHRXd1FHalN4S0pyRG5jLF9SNjBiRGF4TTBqSUdaaUpVcE16cHVyYVhnRHk1UWFmLDEyMDQwNzcyOA0200xaExqNjS?s=ap",
    "invoice_pdf": "https://pay.stripe.com/invoice/acct_1PtWwQGjSxKJrDnc/test_YWNjdF8xUHRXd1FHalN4S0pyRG5jLF9SNjBiRGF4TTBqSUdaaUpVcE16cHVyYVhnRHk1UWFmLDEyMDQwNzcyOA0200xaExqNjS/pdf?s=ap",
    "issuer": {
      "type": "self"
    },
    "last_finalization_error": null,
    "latest_revision": null,
    "lines": {
      "object": "list",
      "data": [
        {
          "id": "il_1QDoa5GjSxKJrDncDIp6LPfF",
          "object": "line_item",
          "amount": -2000,
          "amount_excluding_tax": -2000,
          "currency": "eur",
          "description": "Unused time on SECRag Premium after 25 Oct 2024",
          "discount_amounts": [
          ],
          "discountable": false,
          "discounts": [
          ],
          "invoice": "in_1QDoa5GjSxKJrDncjsfYN40T",
          "invoice_item": "ii_1QDoa5GjSxKJrDncMv9HLXgL",
          "livemode": false,
          "metadata": {
          },
          "period": {
            "end": 1732545057,
            "start": 1729866729
          },
          "plan": {
            "id": "price_1PtWxYGjSxKJrDncZzwjeHQs",
            "object": "plan",
            "active": true,
            "aggregate_usage": null,
            "amount": 2000,
            "amount_decimal": "2000",
            "billing_scheme": "per_unit",
            "created": 1725032520,
            "currency": "eur",
            "interval": "month",
            "interval_count": 1,
            "livemode": false,
            "metadata": {
            },
            "meter": null,
            "nickname": null,
            "product": "prod_Ql33v0kldhhoqs",
            "tiers_mode": null,
            "transform_usage": null,
            "trial_period_days": null,
            "usage_type": "licensed"
          },
          "pretax_credit_amounts": [
          ],
          "price": {
            "id": "price_1PtWxYGjSxKJrDncZzwjeHQs",
            "object": "price",
            "active": true,
            "billing_scheme": "per_unit",
            "created": 1725032520,
            "currency": "eur",
            "custom_unit_amount": null,
            "livemode": false,
            "lookup_key": null,
            "metadata": {
            },
            "nickname": null,
            "product": "prod_Ql33v0kldhhoqs",
            "recurring": {
              "aggregate_usage": null,
              "interval": "month",
              "interval_count": 1,
              "meter": null,
              "trial_period_days": null,
              "usage_type": "licensed"
            },
            "tax_behavior": "unspecified",
            "tiers_mode": null,
            "transform_quantity": null,
            "type": "recurring",
            "unit_amount": 2000,
            "unit_amount_decimal": "2000"
          },
          "proration": true,
          "proration_details": {
            "credited_items": {
              "invoice": "in_1QDoZIGjSxKJrDnc6m6UIHrS",
              "invoice_line_items": [
                "il_1QDoZJGjSxKJrDncGc70N4Xm"
              ]
            }
          },
          "quantity": 1,
          "subscription": "sub_1QDoXVGjSxKJrDncYU0vmavf",
          "subscription_item": "si_R60YaxSr3oVzSg",
          "tax_amounts": [
          ],
          "tax_rates": [
          ],
          "type": "invoiceitem",
          "unit_amount_excluding_tax": "-2000"
        },
        {
          "id": "il_1QDoa5GjSxKJrDncOCzLNtpM",
          "object": "line_item",
          "amount": 10000,
          "amount_excluding_tax": 10000,
          "currency": "eur",
          "description": "1 × SECRag Basic (at €100.00 / year)",
          "discount_amounts": [
          ],
          "discountable": true,
          "discounts": [
          ],
          "invoice": "in_1QDoa5GjSxKJrDncjsfYN40T",
          "livemode": false,
          "metadata": {
          },
          "period": {
            "end": 1761402817,
            "start": 1729866817
          },
          "plan": {
            "id": "price_1PtWy2GjSxKJrDncu1cQMAof",
            "object": "plan",
            "active": true,
            "aggregate_usage": null,
            "amount": 10000,
            "amount_decimal": "10000",
            "billing_scheme": "per_unit",
            "created": 1725032550,
            "currency": "eur",
            "interval": "year",
            "interval_count": 1,
            "livemode": false,
            "metadata": {
            },
            "meter": null,
            "nickname": null,
            "product": "prod_Ql33AItOLX5dZo",
            "tiers_mode": null,
            "transform_usage": null,
            "trial_period_days": null,
            "usage_type": "licensed"
          },
          "pretax_credit_amounts": [
          ],
          "price": {
            "id": "price_1PtWy2GjSxKJrDncu1cQMAof",
            "object": "price",
            "active": true,
            "billing_scheme": "per_unit",
            "created": 1725032550,
            "currency": "eur",
            "custom_unit_amount": null,
            "livemode": false,
            "lookup_key": null,
            "metadata": {
            },
            "nickname": null,
            "product": "prod_Ql33AItOLX5dZo",
            "recurring": {
              "aggregate_usage": null,
              "interval": "year",
              "interval_count": 1,
              "meter": null,
              "trial_period_days": null,
              "usage_type": "licensed"
            },
            "tax_behavior": "unspecified",
            "tiers_mode": null,
            "transform_quantity": null,
            "type": "recurring",
            "unit_amount": 10000,
            "unit_amount_decimal": "10000"
          },
          "proration": false,
          "proration_details": {
            "credited_items": null
          },
          "quantity": 1,
          "subscription": "sub_1QDoXVGjSxKJrDncYU0vmavf",
          "subscription_item": "si_R60YaxSr3oVzSg",
          "tax_amounts": [
          ],
          "tax_rates": [
          ],
          "type": "subscription",
          "unit_amount_excluding_tax": "10000"
        }
      ],
      "has_more": false,
      "total_count": 2,
      "url": "/v1/invoices/in_1QDoa5GjSxKJrDncjsfYN40T/lines"
    },
    "livemode": false,
    "metadata": {
    },
    "next_payment_attempt": null,
    "number": "B65BC86E-0084",
    "on_behalf_of": null,
    "paid": true,
    "paid_out_of_band": false,
    "payment_intent": "pi_3QDoa6GjSxKJrDnc0agQ3WP9",
    "payment_settings": {
      "default_mandate": null,
      "payment_method_options": {
        "acss_debit": null,
        "bancontact": null,
        "card": {
          "request_three_d_secure": "automatic"
        },
        "customer_balance": null,
        "konbini": null,
        "sepa_debit": null,
        "us_bank_account": null
      },
      "payment_method_types": null
    },
    "period_end": 1729866817,
    "period_start": 1729866817,
    "post_payment_credit_notes_amount": 0,
    "pre_payment_credit_notes_amount": 0,
    "quote": null,
    "receipt_number": null,
    "rendering": null,
    "shipping_cost": null,
    "shipping_details": null,
    "starting_balance": 0,
    "statement_descriptor": null,
    "status": "paid",
    "status_transitions": {
      "finalized_at": 1729866817,
      "marked_uncollectible_at": null,
      "paid_at": 1729866927,
      "voided_at": null
    },
    "subscription": "sub_1QDoXVGjSxKJrDncYU0vmavf",
    "subscription_details": {
      "metadata": {
      }
    },
    "subtotal": 8000,
    "subtotal_excluding_tax": 8000,
    "tax": null,
    "test_clock": null,
    "total": 8000,
    "total_discount_amounts": [
    ],
    "total_excluding_tax": 8000,
    "total_pretax_credit_amounts": [
    ],
    "total_tax_amounts": [
    ],
    "transfer_data": null,
    "webhooks_delivered_at": 1729866820
  }
}
"""
)

product_id_bought = response_bought["object"]["lines"]['data'][-1]['price']['id']
product_id_switched = response_switched["object"]["lines"]['data'][-1]['price']['id']
product_id_switched = response_switched_again["object"]["lines"]['data'][-1]['price']['id']

for response in [response_bought, response_switched, response_switched_again]:
    customer_id = response['object']['customer']
    product_id = response['object']['lines']['data'][-1]['price']['id']
    paid = response['object']['amount_paid']

    print(f"Customer ID: {customer_id}, Product ID: {product_id}, paid: {paid}")