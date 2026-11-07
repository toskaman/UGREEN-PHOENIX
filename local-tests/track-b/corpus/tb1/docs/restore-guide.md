# Render node restore notes (Northwind Studio)

If the render node dies, bring a fresh machine back like this: install
the scene file from scenes/shot01.blend, mount the plates folder next
to it, and load the render preset the job was tuned with. The preset
lives at render/preset.yaml — without it the job renders with wrong
exposure and the client rejects the frames.

Last verified by Mara in September.
