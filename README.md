# GardenPi+ - A Program for Controlling Your Irrigation and Monitoring Your Garden
Developed by [<strong>Kenneth Irving (irvingkennet45)</strong>](https://github.com/irvingkennet45 'My Github Profile')

## Overview
The GardenPi+ allows you to control your garden's irrigation system with simple electronics. It's designed to be "plug-and-play" in a sense, so most processes that would require user configuration are easily accessible in JSON config files, meaning that you only need to define a few terms, such as your WiFi SSID and password, and the system will take care of the rest!
## Use Case
## Hardware
With DIY in mind, using an expensive setup would be ridiculous, as the  point of DIY is that it is supposed to be cheaper to create the item at home. With that in mind, you'd be in luck, because with a system like this, you don't even need the best SBCs to get it up and running!

#### Required Hardware
These are some of the components that I used when building my system. The majority of them I had lying around. Decide ahead of time whether or not you're willing to solder your leads, or if you will be using GPIO pins and headers. This will choose what component types you'll be buying.:
- <strong>Raspberry Pi Pico W</strong>
    - <em>Price: $8 </em>
    - Your main logic board. If you decide that soldering is not for you (<em>I don't blame you</em>), then choose a model with pre-soldered headers (<em>Normally something like: "RPi Pico WH"</em>).

- <strong>12V DC Solenoid</strong>
    - <em>Price: $32 </em>
    - The solenoid controls your water flow and only activates upon recieving a 12V signal. With this system, you garden spigot valve will be left open, and will instead be essentially electronically replaced by the solenoid. The recommended size of the solenoid is 3/4". <br> <em>  
    (All garden spigots, at least in the US, are the same thread size. The 3/4" or other measurement refers to the diameter of the hole itself, indicating how much water can pass through it, NOT the compatible threads. A 1/2" and 3/4" will both fit on the same spigot, but the 3/4" will allow more water flow due to it's larger diamter.)</em>

- <strong>Logic-Level MOSFET Module</strong>
    - <em>Price: $8 / for 5 </em>
    - A metal-oxide--thingamajiggy is a type of transistor (an electronic switch) that is one of the most widely used due to its simplicity. Here's a diagram: <br>
    
                      ____________
                     |   MOSFET   |
                     |            |
            12V + -> |VIN [/] VOUT|-> Solenoid + Terminal
            12V - -> |GND [/]  GND|-> Solenoid - Terminal
                     |     ^-<-   | ^
                     |        ^   | |  # The GND > GND and VIN > VOUT ports are gated ([/]) and
               |---->|SIGNAL->|   | ^    controlled by the RPi Pico through GPIO 14
               | |-->|VCC         | |    and the 'signal' pin of the MOSFET. When recieving
               | | |>|GND         | ^    signal on the pin, the MOSFET allows 12V DC through to the solenoid.
               | | | |____________| |
               | | |->->->->->->->-^   # Tie the solenoid & Pico's GND
               | | |  ________           together for signal stability and
               | | | |RPi Pico|          reliabilty
               | | | |        |        
               | | |<|GND     |        
               | |--<|3v3     |        
               |----<|GPIO14  |        
                     |________|

- <strong>Terminal Block</strong>
    - <em>Price: $ </em>
    - Optional, but if it can be bought, you definitely should, as it will be hell cable managing/mounting if you don't. I suggest size of at least 12 ports for future upgrades, but only 5 pairs are officially required, if building a simple system with no extra sensors, and only controlling the solenoid.
- <strong>Relay Module</strong>
    - <em>Price: $ </em>
    - Alternatively, rather than working with a MOSFET, you can use a relay module. Most relays are logic-level to begin with, unlike MOSFETs. The downside is that they are mechanical, and will wear over time, and may need to be replaced. They also make a clicking noise when activating/deactivating, which can be annoying if you have to listen to it.
- <strong>12V Power</strong>
    - <em>Price: $12</em>
    - There are many ways to achieve this. You could use a 12V power adapter that comes with a barrel that has terminal block outputs in order to easily wire it to the rest of your system, or you could use a boost converter, or otherwise, whatever works.
- <strong>25 PSI Regulator</strong>
    - <em>Price: $15</em>
    - This is not technically a must, but it is a probably. Most systems will run over 25 PSI, which could pop tubing and connections, so it's better safe than sorry.
- <strong>Misting Nozzles + Tubing</strong>
    - <em>Price: Varies</em>
    - You obviously need these, but the price can vary, based on your runs, types of nozzles, etc.
- <strong>Misc. Parts</strong>
    - Don't forget to grab some thread tape, mounting hooks, or any other things you might need in order to mount and run your system.

> <strong>Note:</strong> <em>Suggested hardware may vary, depending on climate, if you expand the functionality, etc. For example, for handling more inputs (soil humidity monitors, barometric pressure, etc.), I'd suggest either a Raspberry Pi Pico 2 W or Raspberry Pi Zero W (Generation doesn't matter, you'll have WAY more than enough power and memory either way) simply due to the higher clocks, storage (the RPi 0 would even allow for logging and data retention, as well as serving as a multi-purpose device if desired), memory, etc. You can also use an Arduino to run your system, but note that you'll have to flash MicroPython onto the board, as this software is not compiled in C or C++.</em>

## Features

- Captive portal for easy managament
- OTA updates
- Easy configuration, allowing for plug-n-play
- Expansion capable, although you may have to program such expansions yourself
- Cheap compared to other automated systems
- Extremely customizable
- Weather-aware, allowing the system to pause or alert you in inclement weather situations
- Scheduling features within the portal, for easy automation.

## Security

- Captive portal authentication
- Zero-trust logic, only keeping necessary information open without authentication
- SHA-256 credential hashing, keeping your password, pin, and other such information private
- LAN-only mode if desired
- MAC auto-authentication, allowing for quick access to the portal by referencing a whitelist of MAC address

## Customization

With the ability to full modify direct from the source, you can customize the CSS file to suit your needs!

## Expansion

Add your own modules, such as temperature sensors, humidity sensors, soil monitors, and more, and connect them through GPIO for monitoring and oversight over your garden!

> <strong>Note:</strong> <em>This project was NOT originally intended to be a replacement for the original GardenPi or GardenPi powered by Neptune. I honestly had no idea that these were already programs that existed before I started writing this one, and they might have made creating this easier if I had, but to be fair, this was a personal project to practice my skills. None of the code or concepts used in this project are based off of those, and all though they do share some concepts, all of the ideas that I created for mine are fully from my own knowledge and not CTRL+V. After learning of those projects, I've decided to call it GardenPi+.</em>
>#### OG GardenPi:
> [GardenPi (ankitr42/gardenpi)](https://github.com./ankitr42/gardenpi 'GardenPi') <br>
> [GardenPi powered by Neptune (rjsears/GardenPi)](https://github.com/rjsears/GardenPi 'GardenPi Powered by Neptune')
>
>#### Honorable Mention:
>The Pigrow doesn't technically share the same name as GardenPi, but it is a cool project based on the same concept and has a suite of features:
>
> [Pigrow (Pragmatismo/Pigrow)](https://github.com/Pragmatismo/Pigrow 'Pigrow Project')
