# Docker

Full documentation is [on our wiki](https://www.azerothcore.org/wiki/install-with-docker#installation)

## Building

### Default: incremental server builds (Windows)

The current Esteria workflow uses the persistent `housing-build` container. Reuse
its configured build tree and select the server target instead of building `all`:

```powershell
.\apps\docker\build-server.ps1
.\apps\docker\build-server.ps1 -Target authserver
.\apps\docker\build-server.ps1 -DryRun
```

The default target is `worldserver`; `dbimport` is also supported. This compiles
changed sources and dependencies and links the selected executable. Unrelated
applications and map extractors are excluded. Shared headers can still require
many source files to compile, and static modules still require archiving/linking.

This uses sources already inside the builder: synchronize intended changes there
first. It does not copy this checkout over the builder's separate source tree,
install binaries, package an image, or restart the live server. Keep the existing
build directory; cleaning it or replacing the container loses incremental objects.
The dry run requires Ninja and can stop at a pending CMake regeneration without
showing the subsequent compile steps. Ordinary builds let CMake regenerate as needed.

Check the helper without compiling anything:
`powershell -NoProfile -File apps/docker/test-build-server.ps1` (Docker is mocked).

### Full image builds: initial setup or explicit image rebuilds

For routine Esteria server changes, use the incremental command above. The
following workflow builds service images and is not the default development build.

#### Prerequisites

Ensure that you have docker, docker compose (v2), and the docker buildx command
installed.

It's all bundled with [Docker Desktop](https://docs.docker.com/get-docker/),
though if you're using Linux you can install them through your distribution's
package manage or by using the [documentation from docker](https://docs.docker.com/engine/install/)

#### Running the image build

1. Build containers with command

```console
$ docker compose build
```

    1. Note that the initial build will take a long time, though subsequent builds should be faster

2. Start containers with command

```console
$ docker compose up -d
# Skip the build step
$ docker compose up -d --build
```

    1. Note that this command may take a while the first time, for the database import

3. (on first install) You'll need to attach to the worldserver and create an Admin account

```console
$ docker compose attach ac-worldserver
AC> account create admin password 3 -1
```
