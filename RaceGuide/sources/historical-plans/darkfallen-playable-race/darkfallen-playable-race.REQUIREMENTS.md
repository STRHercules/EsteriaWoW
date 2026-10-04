# Darkfallen playable race requirements

- Add Alliance Darkfallen race `43` and Horde Darkfallen race `44` without changing existing race identities.
- Both races use `0x80000000`; faction behavior must use race ID or team, never that shared mask.
- Use `Darkfallen` as the client filestring, model data `3658`/`3659`, display IDs `60028`/`60029`, Common for 43, and Orcish for 44.
- Reuse the current server plumbing, the supplied Darkfallen assets, and the repository StormLib/WDBC helpers. Do not add dependencies.
- The only active client mutations are additive, collision-checked updates to `G:\3.3.5a - Dev\Data\patch-Z.MPQ` and `G:\3.3.5a - Dev\Data\enUS\patch-enUS-Z.MPQ`; SHA-256 back up both first.
- Preserve all unrelated dirty work. Do not configure or build the server unless separately requested.
- Verify source/staging behavior automatically; live creation, relog, equipment, DB import, and server restart remain separately evidenced operations.
