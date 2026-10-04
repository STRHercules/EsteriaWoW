# races-64-esteria

Runtime WarcraftXL extension for the customized Esteria 3.3.5a client.

It validates the Esteria foundation signature and patch-site fingerprints before allocating or
writing anything, preserves the existing 32-race memory/name data, and expands the runtime tables
to 64 race IDs. It never patches `Wow.exe` on disk.
