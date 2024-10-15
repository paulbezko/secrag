import eventlet
eventlet.monkey_patch()
class Config:
    DB_NAME="postgres"
    DB_USER="postgres.qjgjqswlonxuhmiiwddj"
    DB_HOST="aws-0-eu-central-1.pooler.supabase.com"
    DB_PORT="6543"
    DB_PASS="D9XkIu7J$3$#8/xN"

    FLASK_KEY_SECRET="9z2{_87.l5o0s@D9/o0eX.1QlJ8%]tcY-IXEo}Z*p^eQc_[DiC7xN8x+jHB$F0PE"
    JWT_SECRET="G2B8oiHrZcH4839Qj+W7SmZyfoxuopZYL4d0yypUs9ERtld0751Q2twSTuXq5tW6tKILhQK2SrKnjqqiAQGAXQ=="

    MAIL_SENDER_USER="secrag.info@gmail.com"
    MAIL_SENDER_PASS="irebkoiuwlwywsco"

    STRIPE_KEY_TEST="sk_test_51PtWwQGjSxKJrDncR8txeoTyxjbtQTuiABZkui2zNjIfwozW3VQarB6wC3ZMfPOrKvnjGCfAv47osfJcwGqcFllU00BP82NBcK"
    STRIPE_WEBHOOK_KEY_TEST="whsec_294fb3df5948c6d347054e57f0c85e3e2a671d7675ce66e97b5f726c5bd73ae9"
    STRIPE_PRODUCT_BASIC_MONTHLY="price_1PtWxIGjSxKJrDncAmBA32TK"
    STRIPE_PRODUCT_BASIC_YEARLY="price_1PtWy2GjSxKJrDncu1cQMAof"
    STRIPE_PRODUCT_PREMIUM_MONTHLY="price_1PtWxYGjSxKJrDncZzwjeHQs"
    STRIPE_PRODUCT_PREMIUM_YEARLY="price_1PtWxpGjSxKJrDncABN5kg0P"
    STRIPE_PRODUCT_REPLENISH="price_1Q6EHfGjSxKJrDncoTy51b5p"

    SUPABASE_URL="https://qjgjqswlonxuhmiiwddj.supabase.co"
    SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqZ2pxc3dsb254dWhtaWl3ZGRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjUwMzMxOTUsImV4cCI6MjA0MDYwOTE5NX0.UtkJnnQsOHUEcrvXzpzJ9nCQOhh-RypSYvQBvVMiyUw"

    OPENAI_API_KEY="sk-proj-0U1etEdNPyfN0tEvklyVT3BlbkFJ0899XXITmyGhvlsfA7eS"

    REDIRECT_URL="https://secrag.com"