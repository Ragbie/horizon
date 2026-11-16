"""`late tick beside orb`: fresh primed TNT and falling blocks tick when an orb joined after them (#17269)."""

GROUP = 'late tick beside orb'


def cases(cmd, setup):
    """`ServerLevel.tick` ticks every entity in its tick list once a tick, in join order. Three primed TNT
    and a falling block are summoned, then an experience orb; after one tick each fuse is down by one and
    the falling block's `Time` up by one. A control area holds the same without the orb."""
    x0, y0, z0 = 6240, 250, 6240
    # Entities tick once every chunk within 2 columns is loaded (ChunkMap.prepareEntityTickingChunk).
    chunk = [[(x0 >> 4) + dx, (z0 >> 4) + dz] for dx in range(-2, 3) for dz in range(-2, 3)]
    ops = [cmd(f'/forceload add {x0} {z0}', False), {'op': 'wait_chunks', 'chunks': chunk},
           cmd(f'/fill {x0} {y0 - 1} {z0} {x0 + 15} {y0 - 1} {z0 + 15} stone', expect_result=256)]
    uuids = []
    for area, orb in ((0, True), (8, False)):
        for n in range(1, 4):
            uuids.append((f'000043c5-0000-0000-{area:04x}-{n:04x}00000001', 'fuse'))
            ops.append(cmd(f'/summon tnt {x0 + 3 * n}.5 {y0} {z0 + area + 2}.5 '
                           f'{{UUID:[I;17269,{area},{n},1],fuse:400}}', expect_result=1))
        uuids.append((f'000043c5-0000-0000-{area:04x}-000400000001', 'Time'))
        ops.append(cmd(f'/summon falling_block {x0 + 12}.5 {y0} {z0 + area + 2}.5 '
                       f'{{UUID:[I;17269,{area},4,1],BlockState:{{Name:"minecraft:sand"}},Time:1,NoGravity:1b}}',
                       expect_result=1))
        if orb:
            ops.append(cmd(f'/summon experience_orb {x0 + 12}.5 {y0} {z0 + area + 5}.5 {{Value:3}}',
                           expect_result=1))

    def reads():
        for uuid, key in uuids:
            ops.append(cmd(f'/data get entity {uuid} {key}'))

    reads()
    ops.append({'op': 'tick', 'n': 1})
    reads()
    ops.append({'op': 'tick', 'n': 1})
    reads()
    return ops + setup(f'/kill @e[type=!player,x={x0},y={y0 - 8},z={z0},dx=16,dy=24,dz=16]',
                       f'/fill {x0} {y0 - 1} {z0} {x0 + 15} {y0 - 1} {z0 + 15} air',
                       f'/forceload remove {x0} {z0}')
