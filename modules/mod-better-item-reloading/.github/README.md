# ![logo](https://raw.githubusercontent.com/azerothcore/azerothcore.github.io/master/images/logo-github.png) AzerothCore

## BetterItemReloading

- Latest build status with azerothcore:

[![Build Status](https://github.com/azerothcore/mod-better-item-reloading/workflows/core-build/badge.svg?branch=master&event=push)](https://github.com/azerothcore/mod-better-item-reloading)

BetterItemReloading is a C++ Azerothcore module which allows to reload items on the server side and as much as possible on the client side of WoW 3.3.5.

Sadly some things are cached on the client which can't be properly invalidated and need DBC file changes.

The following things must be changed in DBC files:

* ItemClass
* ItemSubClass
* sound_override_subclassid
* MaterialID
* ItemDisplayInfo
* InventorySlotID
* SheathID

Multiple items can be reloaded by splitting each entry id with a space like: .breload item 12345 23456 34567

Here's an example how i change an item on the fly in the database and reload it without restarting anything:

<p>
    <img src="Example.gif" height="747" width="595" />
</p>
