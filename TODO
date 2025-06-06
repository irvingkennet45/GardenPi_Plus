# TODO

This is the TODO list for the GardenPi+ project.

## Current Stage

<strong>Active:</strong> Yes <br>
<strong>First Commit:</strong> June 4th, 2025 <br>
<strong>Active Pull Requests:</strong> No <br>
<strong>Last Updated:</strong> June 5th, 2025 <br>

<strong>Working:</strong> Functionality severly limited

<strong>Issue Summary:</strong> Alpha build, bare necessities are functioning currently. Massive security concerns. Do not use as is; check back later. - @irvingkennet45

> <strong>Version:</strong> GardenPi+ v1.0 (Public Release 1) [Alpha Build]

## Content

- [ ] Functional Auth Portal
    - [ ] Browser Cookies for Persistent Sessions
    - [ ] MAC Auto- Authentication
- [ ] Weather API Integration
    - [ ] Live Weather Map (if possible)
    - [ ] 3-week Persistent Weather Data Logging
    - [ ] Weather-aware Misting Automation
- [ ] Create a "sleep" mode
- [ ] Add a REPL console in the web portal
- [ ] Enable the ability for Over-the-Air (OTA) updates
- [ ] Create security dependencies for the device (e.g. zero-trust architecture, only opening necessary ports)
- [ ] Request hardware information from device for the "About" page.
    - [ ] Periodically request internal sensor updates, such as temperature, storage free, etc.
- [ ] Configure trustworthiness so that browsers enable the use of all permissions.
    - [ ] Potentially requires automated SSL certificate creation
    - [ ] Progressive Web App, if possible
- [ ] Add a README file within the /logic directory for documentation and user guidance


## Debugging

- [ ] Fix the favicon not displaying when running the webserver on the Pico
- [ ] Either replace with a regular image file, or fix the way the .gif Logo is displayed

## Changes

- [ ] Add a looping boot in case of outages, or failed connection
    - [ ] Stagger WiFi loop for every 5 minutes after 10 tries.
- [ ] Run main.py on boot
- [ ] Cache images and other large media in the client's browser in order to offload the Pico already-limited RAM overhead.
    - [ ] Potentially store images in a public cloud, or even in the repository to free up space.
- [ ] Clean-ip files, getting rid of extra and unecessary fluff, as well as better organization

## Release

- [x] Initialize the repoistory
- [x] Publish the repository publicly
- [x] Reach an "alpha" build
- [ ] Compile versions into drag-n-drop projects for ease of use
    - [ ] Create a desktop installer, allowing for the Pico to be flashed and the GardenPi+ to be configured before upload. (Requires C)

## Done

- [x] Update project README
- [x] Create the scheduling function
- [x] Create the toggling function
- [x] Finish "alpha" styling
- [x] Change NTP request to every hour
