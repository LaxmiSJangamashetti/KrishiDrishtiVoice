# Mandi Price API Specification

Base URL: `https://mandi-api.onrender.com/v1`

The service is unauthenticated and rate-limited to 100 requests per 15 minutes per IP. It provides `/states`, `/commodities`, `/markets`, `/prices`, and `/prices/history` JSON envelopes. Prices are INR per quintal. The application must display only returned observations and their arrival dates; examples in the owner specification are not live prices.
