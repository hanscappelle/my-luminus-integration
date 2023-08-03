# My Luminus Integration for Home Assistant

This project is an attempt to create an integration to consume services provided by
My Luminus Apps for contract and metering management.

## How

All you need for this integration to work is your My Luminus login

Currently working on getting this project published to HACS
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

For now you either have to install it manually by dropping the custom_components
folder contents into your HA installation. Or by adding this repo as a custom
repo within HACS. For that, within HACS just select "add repo" then pick "integration"
as type and enter a name and the url of this repo. Or read here https://hacs.xyz/docs/faq/custom_repositories/

Then you can add a new integration, search for "My Luminus" to find this one:

![add integration](screenshots/Screenshot%202023-07-30%20at%2013.22.26.png)

Next you'll get a quick installation wizard, enter your credentials here:

![configuration wizard](screenshots/Screenshot%202023-07-30%20at%2013.22.36.png)

Once done this integration should be visible:

![shows integration](screenshots/Screenshot%202023-07-30%20at%2013.23.09.png)

An example of all the data it fetches:

![fetched data example](screenshots/Screenshot%202023-07-30%20at%2013.19.36.png)

## Why?

Because we can!

## Limitations

For now just some sensors, still figuring out how to push data to the api from within HA.

## Version History

# 0.1.0

initial version

* get token
* get budget lines and create some sensors