# My Luminus - Pricing (Unofficial)

Get gas and electricity pricing from your active contracts in My Luminus (variable or fixed rates only). Adds a Home Assistant device for each EAN meter with daily data refresh. Use the exposed entities to configure energy cost in your HA Energy dashboard.

## Installation (via HACS)

1. Add this repository as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) in HACS.
2. Install "My Luminus - Pricing".
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration** and choose "My Luminus - Pricing".
5. Enter your My Luminus username and password.
6. Assign EAN devices to areas.

## Energy dashboard

In **Settings → Energy**, configure your grid consumption and bind the cost of consumed energy to one of the Luminus pricing entities.

## Disclaimer

This integration is unofficial and not supported by Luminus. Use at your own risk.
